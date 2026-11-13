import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.cadastrar_usuario import CadastrarUsuario
from app.application.casos_de_uso.contribuicoes.carregar_logradouros import CarregarLogradouros
from app.application.casos_de_uso.encaminhamentos.avisos import AvisosDoCiclo
from app.application.casos_de_uso.encaminhamentos.encaminhar_prioritarias import (
    LIMITE_PADRAO_POR_EXECUCAO,
    EncaminharPrioritarias,
    MotivoParaPular,
    PedidoAutomatico,
)
from app.application.casos_de_uso.encaminhamentos.lembrete import LembrarOrgaos
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.casos_de_uso.importacoes.importar_pelo_terminal import (
    ImportacaoPendente,
    ImportarPeloTerminal,
)
from app.application.casos_de_uso.redefinir_senha import RedefinirSenha
from app.application.portas.importacoes import ArquivoRecebido, OrigensDeDados
from app.application.sessoes import GestaoDeSessoes
from app.domain.erros import (
    EmailInvalido,
    EmailJaCadastrado,
    ErroDeDominio,
    OrigemIndisponivel,
    OrigemRecusada,
    UsuarioNaoEncontrado,
)
from app.domain.prioridade import NOTA_ALTA, FonteDaFila
from app.domain.usuario import PERFIS_DA_GESTAO, Perfil
from app.infrastructure.auth.senhas import HashDeSenhaArgon2
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.db.conexao import criar_fabrica_de_sessoes
from app.infrastructure.email.montagem import montar_envio_de_email
from app.infrastructure.encaminhamento.avisos import AvisosPorEmail
from app.infrastructure.encaminhamento.despacho import montar_despacho
from app.infrastructure.importacao.leitores import LeitorDeArquivos
from app.infrastructure.importacao.montagem import (
    FilaImediata,
    montar_origens_de_dados,
    montar_servicos_de_importacao,
)
from app.infrastructure.relogio import RelogioDoSistema
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
from app.infrastructure.repositories.avisos import DestinatariosDosAvisosSql
from app.infrastructure.repositories.contribuicoes import ReferenciaDoFormularioSql
from app.infrastructure.repositories.encaminhamentos import EncaminhamentoRepositorySql
from app.infrastructure.repositories.prioridade import PrioridadeRepositorySql
from app.infrastructure.repositories.referencias import ReferenciasSql
from app.infrastructure.repositories.sessoes import SessaoRepositorySql
from app.infrastructure.repositories.usuarios import UsuarioRepositorySql
from app.infrastructure.settings import Configuracao, carregar_configuracao

MENSAGEM_DE_ORIGEM_INDISPONIVEL = "A origem não respondeu. Confira o endereço ou a conexão."
MENSAGENS_DE_ERRO: dict[type[ErroDeDominio], str] = {
    EmailInvalido: "O e-mail informado não é válido.",
    EmailJaCadastrado: "Já existe uma conta com este e-mail.",
    UsuarioNaoEncontrado: "Não existe conta com este e-mail.",
}


def main(argumentos: Sequence[str] | None = None) -> int:
    comando = _ler_comando(argumentos)
    configuracao = carregar_configuracao()
    fabrica = criar_fabrica_de_sessoes(configuracao.url_do_banco)
    if comando.comando == "importar":
        return _importar(comando, configuracao, fabrica)
    if comando.comando == "carregar-logradouros":
        return _carregar_logradouros(comando, fabrica)
    if comando.comando == "encaminhar-prioritarias":
        return _encaminhar_prioritarias(comando, configuracao, fabrica)
    if comando.comando == "lembrar-orgaos":
        return _lembrar_orgaos(configuracao, fabrica)
    try:
        with fabrica.begin() as sessao:
            if comando.comando == "cadastrar-usuario":
                _cadastrar_usuario(sessao, comando)
            else:
                _redefinir_senha(sessao, comando, configuracao)
    except ErroDeDominio as erro:
        print(MENSAGENS_DE_ERRO.get(type(erro), "Operação recusada."), file=sys.stderr)
        return 1
    return 0


def _ler_comando(argumentos: Sequence[str] | None) -> argparse.Namespace:
    leitor = argparse.ArgumentParser(prog="recifeview", description="Administra os acessos.")
    comandos = leitor.add_subparsers(dest="comando", required=True)

    cadastro = comandos.add_parser("cadastrar-usuario", help="Cria uma conta com senha temporária")
    cadastro.add_argument("--email", required=True)
    cadastro.add_argument("--nome", required=True)
    cadastro.add_argument(
        "--perfil",
        choices=[perfil.value for perfil in Perfil if perfil in PERFIS_DA_GESTAO],
        default=Perfil.GESTOR.value,
    )

    redefinicao = comandos.add_parser("redefinir-senha", help="Gera uma nova senha temporária")
    redefinicao.add_argument("--email", required=True)

    importacao = comandos.add_parser(
        "importar", help="Importa um arquivo, um endereço permitido ou uma consulta a um banco"
    )
    origem = importacao.add_mutually_exclusive_group(required=True)
    origem.add_argument("--arquivo", type=Path)
    origem.add_argument("--endereco", help="Endereço https de um host de API_HOSTS_DE_IMPORTACAO")
    origem.add_argument("--banco", help="Nome de uma conexão de API_BANCOS_DE_ORIGEM")
    importacao.add_argument("--consulta", help="SELECT a rodar no banco, com --banco")
    importacao.add_argument(
        "--data-do-retrato",
        required=True,
        type=date.fromisoformat,
        help="Dia em que o arquivo foi baixado (AAAA-MM-DD)",
    )
    importacao.add_argument(
        "--carga-inicial",
        action="store_true",
        help="Primeira carga da base: não compara com o que já existe",
    )

    logradouros = comandos.add_parser(
        "carregar-logradouros", help="Monta a lista de vias a partir de arquivos públicos do 156"
    )
    logradouros.add_argument("--arquivo", required=True, type=Path, action="append")

    automatico = comandos.add_parser(
        "encaminhar-prioritarias",
        help="Encaminha as ocorrências de nota alta ao órgão sugerido (para o agendador)",
    )
    automatico.add_argument(
        "--fonte", choices=[fonte.value for fonte in FonteDaFila], default=FonteDaFila.CENTRAL_156
    )
    automatico.add_argument("--nota-minima", type=float, default=NOTA_ALTA)
    automatico.add_argument("--limite", type=int, default=LIMITE_PADRAO_POR_EXECUCAO)

    comandos.add_parser(
        "lembrar-orgaos",
        help="Lembra o órgão dos encaminhamentos com prazo vencido (para o agendador)",
    )
    return leitor.parse_args(argumentos)


def _importar(
    comando: argparse.Namespace, configuracao: Configuracao, fabrica: sessionmaker[Session]
) -> int:
    servicos = montar_servicos_de_importacao(configuracao, fabrica, FilaImediata())
    importar = ImportarPeloTerminal(servicos)
    try:
        arquivo = _receber_da_origem(comando, montar_origens_de_dados(configuracao, servicos))
        if arquivo is None:
            importacao = importar.executar(
                comando.arquivo, comando.data_do_retrato, comando.carga_inicial
            )
        else:
            importacao = importar.executar_recebido(
                arquivo, comando.data_do_retrato, comando.carga_inicial
            )
    except OrigemRecusada as recusa:
        print(recusa.motivo, file=sys.stderr)
        return 1
    except OrigemIndisponivel:
        print(MENSAGEM_DE_ORIGEM_INDISPONIVEL, file=sys.stderr)
        return 1
    except ImportacaoPendente as pendente:
        print(
            f"A importação {pendente.importacao_id} tem pendências. Responda pelo painel.",
            file=sys.stderr,
        )
        return 1
    print(f"Importação {importacao.id}: {importacao.status.value}")
    print(importacao.mensagem_de_erro or json.dumps(importacao.resultado, ensure_ascii=False))
    return 0


def _receber_da_origem(
    comando: argparse.Namespace, origens: OrigensDeDados
) -> ArquivoRecebido | None:
    if comando.endereco:
        return origens.por_endereco.baixar(comando.endereco)
    if comando.banco:
        return origens.por_banco.extrair(comando.banco, comando.consulta or "")
    return None


def _carregar_logradouros(comando: argparse.Namespace, fabrica: sessionmaker[Session]) -> int:
    leitor = LeitorDeArquivos()
    tabelas = [leitor.abrir(caminho) for caminho in comando.arquivo]
    bairros = ReferenciasSql(fabrica).carregar().bairros
    carga = CarregarLogradouros(ReferenciaDoFormularioSql(fabrica))
    print(f"Vias somadas à lista: {carga.executar(tabelas, bairros)}")
    return 0


def _servicos_de_encaminhamento(
    sessao: Session, configuracao: Configuracao
) -> ServicosDeEncaminhamento:
    emails = montar_envio_de_email(configuracao)
    avisos = AvisosDoCiclo(
        DestinatariosDosAvisosSql(sessao), AvisosPorEmail(emails), configuracao.endereco_do_site
    )
    return ServicosDeEncaminhamento(
        EncaminhamentoRepositorySql(sessao),
        montar_despacho(configuracao, emails),
        RelogioDoSistema(),
        avisos,
    )


def _encaminhar_prioritarias(
    comando: argparse.Namespace, configuracao: Configuracao, fabrica: sessionmaker[Session]
) -> int:
    with fabrica.begin() as sessao:
        servicos = _servicos_de_encaminhamento(sessao, configuracao)
        caso = EncaminharPrioritarias(servicos, PrioridadeRepositorySql(sessao))
        pedido = PedidoAutomatico(FonteDaFila(comando.fonte), comando.nota_minima, comando.limite)
        resultado = caso.executar(pedido)
    print(f"Candidatas com nota a partir de {pedido.nota_minima:g}: {resultado.candidatas}")
    print(f"Encaminhadas: {len(resultado.encaminhadas)} (falhas no canal: {resultado.falhas})")
    print(f"Já tinham encaminhamento aberto: {resultado.puladas[MotivoParaPular.JA_ENCAMINHADA]}")
    print(f"Sem órgão sugerido: {resultado.puladas[MotivoParaPular.SEM_SUGESTAO]}")
    return 0


def _lembrar_orgaos(configuracao: Configuracao, fabrica: sessionmaker[Session]) -> int:
    with fabrica.begin() as sessao:
        resultado = LembrarOrgaos(_servicos_de_encaminhamento(sessao, configuracao)).executar()
    print(f"Lembretes enviados: {resultado.enviados} (falhas no canal: {resultado.falhas})")
    return 0


def _cadastrar_usuario(sessao: Session, comando: argparse.Namespace) -> None:
    cadastro = CadastrarUsuario(UsuarioRepositorySql(sessao), HashDeSenhaArgon2())
    resultado = cadastro.executar(comando.email, comando.nome, Perfil(comando.perfil))
    usuario = resultado.usuario
    print(f"Conta criada: {usuario.nome} <{usuario.email}> ({usuario.perfil.value})")
    _mostrar_senha_temporaria(resultado.senha_temporaria)


def _redefinir_senha(
    sessao: Session, comando: argparse.Namespace, configuracao: Configuracao
) -> None:
    relogio = RelogioDoSistema()
    emissor = EmissorDeTokenJwt(configuracao.segredo_jwt.get_secret_value(), timedelta(minutes=1))
    redefinicao = RedefinirSenha(
        UsuarioRepositorySql(sessao),
        HashDeSenhaArgon2(),
        GestaoDeSessoes(SessaoRepositorySql(sessao), emissor, relogio),
        RegistroDeAcessosSql(sessao),
        relogio,
    )
    _mostrar_senha_temporaria(redefinicao.executar(comando.email))


def _mostrar_senha_temporaria(senha: str) -> None:
    print(f"Senha temporária: {senha}")
    print("Entregue a senha por um canal seguro. Ela precisa ser trocada no primeiro acesso.")


if __name__ == "__main__":
    sys.exit(main())
