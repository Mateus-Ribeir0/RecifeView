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


class ImportacaoNaoEncontrada(ErroDeDominio):
    pass


class ImportacaoEmEstadoInvalido(ErroDeDominio):
    pass


class ImportacaoNaoPodeSerDesfeita(ErroDeDominio):
    pass


class ArquivoVazio(ErroDeDominio):
    pass


class ArquivoIlegivel(ErroDeDominio):
    pass


class ArquivoGrandeDemais(ErroDeDominio):
    pass


class DecisaoInvalida(ErroDeDominio):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class PeriodoInvalido(ErroDeDominio):
    pass


class ValorDeFiltroInvalido(ErroDeDominio):
    pass


class DiaForaDaJanela(ErroDeDominio):
    pass


class CadastroInvalido(ErroDeDominio):
    def __init__(self, campo: str, motivo: str) -> None:
        super().__init__(motivo)
        self.campo = campo
        self.motivo = motivo


class AcessoNegado(ErroDeDominio):
    pass


class AreaDaGestaoNegada(ErroDeDominio):
    pass


class CodigoInvalido(ErroDeDominio):
    pass


class TentativasDemais(ErroDeDominio):
    pass


class ContribuicaoInvalida(ErroDeDominio):
    def __init__(self, campo: str, motivo: str) -> None:
        super().__init__(motivo)
        self.campo = campo
        self.motivo = motivo


class EnviosDemais(ErroDeDominio):
    pass


class ParNaoEncontrado(ErroDeDominio):
    pass


class PenteFinoPendente(ErroDeDominio):
    pass


class PacoteVazio(ErroDeDominio):
    pass


class ProtocoloInvalido(ErroDeDominio):
    pass


class OcorrenciaNaoEncontrada(ErroDeDominio):
    pass


class OcorrenciaJaEncaminhada(ErroDeDominio):
    pass


class EncaminhamentoNaoEncontrado(ErroDeDominio):
    pass


class EncaminhamentoInvalido(ErroDeDominio):
    def __init__(self, campo: str, motivo: str) -> None:
        super().__init__(motivo)
        self.campo = campo
        self.motivo = motivo


class TransicaoInvalida(ErroDeDominio):
    pass


class LinkDeRetornoInvalido(ErroDeDominio):
    pass


class LimiteDePedidosAtingido(ErroDeDominio):
    pass
