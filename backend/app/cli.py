import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.cadastrar_usuario import CadastrarUsuario
from app.application.casos_de_uso.contribuicoes.carregar_logradouros import CarregarLogradouros
from app.application.casos_de_uso.importacoes.importar_pelo_terminal import (
    ImportacaoPendente,
    ImportarPeloTerminal,
)
from app.application.casos_de_uso.redefinir_senha import RedefinirSenha
from app.application.sessoes import GestaoDeSessoes
from app.domain.erros import EmailInvalido, EmailJaCadastrado, ErroDeDominio, UsuarioNaoEncontrado
from app.domain.usuario import PERFIS_DA_GESTAO, Perfil
from app.infrastructure.auth.senhas import HashDeSenhaArgon2
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.db.conexao import criar_fabrica_de_sessoes
from app.infrastructure.importacao.leitores import LeitorDeArquivos
from app.infrastructure.importacao.montagem import (
    FilaImediata,
    montar_servicos_de_importacao,
)
from app.infrastructure.relogio import RelogioDoSistema
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
from app.infrastructure.repositories.contribuicoes import ReferenciaDoFormularioSql
from app.infrastructure.repositories.referencias import ReferenciasSql
from app.infrastructure.repositories.sessoes import SessaoRepositorySql
from app.infrastructure.repositories.usuarios import UsuarioRepositorySql
from app.infrastructure.settings import Configuracao, carregar_configuracao

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

    importacao = comandos.add_parser("importar", help="Importa um arquivo pelo terminal")
    importacao.add_argument("--arquivo", required=True, type=Path)
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
    return leitor.parse_args(argumentos)


def _importar(
    comando: argparse.Namespace, configuracao: Configuracao, fabrica: sessionmaker[Session]
) -> int:
    servicos = montar_servicos_de_importacao(configuracao, fabrica, FilaImediata())
    importar = ImportarPeloTerminal(servicos)
    try:
        importacao = importar.executar(
            comando.arquivo, comando.data_do_retrato, comando.carga_inicial
        )
    except ImportacaoPendente as pendente:
        print(
            f"A importação {pendente.importacao_id} tem pendências. Responda pelo painel.",
            file=sys.stderr,
        )
        return 1
    print(f"Importação {importacao.id}: {importacao.status.value}")
    print(importacao.mensagem_de_erro or json.dumps(importacao.resultado, ensure_ascii=False))
    return 0


def _carregar_logradouros(comando: argparse.Namespace, fabrica: sessionmaker[Session]) -> int:
    leitor = LeitorDeArquivos()
    tabelas = [leitor.abrir(caminho) for caminho in comando.arquivo]
    bairros = ReferenciasSql(fabrica).carregar().bairros
    carga = CarregarLogradouros(ReferenciaDoFormularioSql(fabrica))
    print(f"Vias somadas à lista: {carga.executar(tabelas, bairros)}")
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
