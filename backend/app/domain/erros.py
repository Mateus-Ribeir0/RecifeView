from datetime import datetime


class ErroDeDominio(Exception):
    pass


class EmailInvalido(ErroDeDominio):
    pass


class EmailJaCadastrado(ErroDeDominio):
    pass


class UsuarioNaoEncontrado(ErroDeDominio):
    pass


class CredenciaisInvalidas(ErroDeDominio):
    pass


class ContaInativa(ErroDeDominio):
    pass


class ContaBloqueada(ErroDeDominio):
    def __init__(self, desbloqueio_em: datetime) -> None:
        super().__init__(desbloqueio_em.isoformat())
        self.desbloqueio_em = desbloqueio_em


class SessaoInvalida(ErroDeDominio):
    pass


class SenhaAtualIncorreta(ErroDeDominio):
    pass


class SenhaFraca(ErroDeDominio):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo
