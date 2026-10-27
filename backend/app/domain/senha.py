from app.domain.email import Email
from app.domain.erros import SenhaFraca

TAMANHO_MINIMO_DA_SENHA = 12
TAMANHO_MAXIMO_DA_SENHA = 128
TAMANHO_MINIMO_DO_NOME_DE_USUARIO_COMPARADO = 4


def validar_nova_senha(senha: str, email: Email) -> None:
    if len(senha) < TAMANHO_MINIMO_DA_SENHA:
        raise SenhaFraca(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_DA_SENHA} caracteres.")
    if len(senha) > TAMANHO_MAXIMO_DA_SENHA:
        raise SenhaFraca(f"A senha pode ter no máximo {TAMANHO_MAXIMO_DA_SENHA} caracteres.")
    if len(set(senha)) == 1:
        raise SenhaFraca("A senha não pode ser um único caractere repetido.")
    if _contem_nome_de_usuario(senha, email):
        raise SenhaFraca("A senha não pode conter a parte do seu e-mail antes do @.")


def _contem_nome_de_usuario(senha: str, email: Email) -> bool:
    nome = email.nome_de_usuario
    return len(nome) >= TAMANHO_MINIMO_DO_NOME_DE_USUARIO_COMPARADO and nome in senha.lower()
