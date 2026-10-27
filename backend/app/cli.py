import argparse
import sys
from collections.abc import Sequence
from datetime import timedelta

from sqlalchemy.orm import Session

from app.application.casos_de_uso.cadastrar_usuario import CadastrarUsuario
from app.application.casos_de_uso.redefinir_senha import RedefinirSenha
from app.application.sessoes import GestaoDeSessoes
from app.domain.erros import EmailInvalido, EmailJaCadastrado, ErroDeDominio, UsuarioNaoEncontrado
from app.domain.usuario import Perfil
from app.infrastructure.auth.senhas import HashDeSenhaArgon2
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.db.conexao import criar_fabrica_de_sessoes
from app.infrastructure.relogio import RelogioDoSistema
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
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
        "--perfil", choices=[perfil.value for perfil in Perfil], default=Perfil.GESTOR.value
    )

    redefinicao = comandos.add_parser("redefinir-senha", help="Gera uma nova senha temporária")
    redefinicao.add_argument("--email", required=True)
    return leitor.parse_args(argumentos)


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
