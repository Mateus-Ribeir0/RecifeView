from dataclasses import dataclass
from uuid import uuid4

from app.application.portas.seguranca import HashDeSenha
from app.application.portas.usuarios import UsuarioRepository
from app.application.senhas_temporarias import gerar_senha_temporaria
from app.domain.email import Email
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import CadastroInvalido, EmailJaCadastrado
from app.domain.usuario import Perfil, Usuario


@dataclass(frozen=True)
class DadosDoCadastro:
    email: str
    nome: str
    perfil: Perfil = Perfil.GESTOR
    orgao: Orgao | None = None


@dataclass(frozen=True)
class CadastroRealizado:
    usuario: Usuario
    senha_temporaria: str


def _exigir_orgao_so_na_conta_corporativa(dados: DadosDoCadastro) -> None:
    e_corporativa = dados.perfil is Perfil.CORPORATIVO
    if e_corporativa and dados.orgao is None:
        raise CadastroInvalido("orgao", "Informe o órgão da conta corporativa.")
    if not e_corporativa and dados.orgao is not None:
        raise CadastroInvalido("orgao", "Só a conta corporativa tem órgão.")


@dataclass(frozen=True)
class CadastrarUsuario:
    """Pela linha de comando, a conta nasce com senha temporária e troca no primeiro acesso."""

    usuarios: UsuarioRepository
    senhas: HashDeSenha

    def executar(self, dados: DadosDoCadastro) -> CadastroRealizado:
        _exigir_orgao_so_na_conta_corporativa(dados)
        endereco = Email(dados.email)
        if self.usuarios.buscar_por_email(endereco) is not None:
            raise EmailJaCadastrado
        senha_temporaria = gerar_senha_temporaria()
        usuario = Usuario(
            id=uuid4(),
            email=endereco,
            nome=dados.nome.strip(),
            perfil=dados.perfil,
            hash_da_senha=self.senhas.gerar(senha_temporaria),
            orgao=dados.orgao,
        )
        self.usuarios.adicionar(usuario)
        return CadastroRealizado(usuario, senha_temporaria)
