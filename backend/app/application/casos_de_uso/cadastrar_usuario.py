from dataclasses import dataclass
from uuid import uuid4

from app.application.portas.seguranca import HashDeSenha
from app.application.portas.usuarios import UsuarioRepository
from app.application.senhas_temporarias import gerar_senha_temporaria
from app.domain.email import Email
from app.domain.erros import EmailJaCadastrado
from app.domain.usuario import Perfil, Usuario


@dataclass(frozen=True)
class CadastroRealizado:
    usuario: Usuario
    senha_temporaria: str


@dataclass(frozen=True)
class CadastrarUsuario:
    usuarios: UsuarioRepository
    senhas: HashDeSenha

    def executar(self, email: str, nome: str, perfil: Perfil) -> CadastroRealizado:
        endereco = Email(email)
        if self.usuarios.buscar_por_email(endereco) is not None:
            raise EmailJaCadastrado
        senha_temporaria = gerar_senha_temporaria()
        usuario = Usuario(
            id=uuid4(),
            email=endereco,
            nome=nome.strip(),
            perfil=perfil,
            hash_da_senha=self.senhas.gerar(senha_temporaria),
        )
        self.usuarios.adicionar(usuario)
        return CadastroRealizado(usuario, senha_temporaria)
