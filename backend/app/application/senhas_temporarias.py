import secrets

BYTES_DA_SENHA_TEMPORARIA = 12


def gerar_senha_temporaria() -> str:
    return secrets.token_urlsafe(BYTES_DA_SENHA_TEMPORARIA)
