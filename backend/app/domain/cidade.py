from enum import StrEnum

from app.domain.importacao.pseudonimizacao import numero_foi_informado

DIAS_DA_VISAO_DO_CIDADAO = 90
TAMANHO_DA_FAIXA_DE_NUMERACAO = 100


class SituacaoPublica(StrEnum):
    RECEBIDO = "recebido"
    EM_ANALISE = "em_analise"
    NO_PAINEL = "no_painel"
    COBERTO_POR_PEDIDO_OFICIAL = "coberto_por_pedido_oficial"


SITUACOES_PUBLICAS = {
    "aberta": SituacaoPublica.RECEBIDO,
    "em_pacote": SituacaoPublica.EM_ANALISE,
    "na_base": SituacaoPublica.NO_PAINEL,
    "retirada": SituacaoPublica.COBERTO_POR_PEDIDO_OFICIAL,
}


def situacao_publica(situacao: str, tem_dupla_aberta: bool) -> SituacaoPublica:
    publica = SITUACOES_PUBLICAS.get(situacao, SituacaoPublica.RECEBIDO)
    if publica is SituacaoPublica.RECEBIDO and tem_dupla_aberta:
        return SituacaoPublica.EM_ANALISE
    return publica


def faixa_de_numeracao(numero: str | None) -> str | None:
    """O número exato pode ser a casa de quem relatou: o cidadão vê só a centena."""
    if numero is None or not numero_foi_informado(numero):
        return None
    digitos = "".join(caractere for caractere in numero if caractere.isdigit())
    if not digitos:
        return None
    inicio = int(digitos) // TAMANHO_DA_FAIXA_DE_NUMERACAO * TAMANHO_DA_FAIXA_DE_NUMERACAO
    fim = inicio + TAMANHO_DA_FAIXA_DE_NUMERACAO - 1
    return f"entre {max(inicio, 1)} e {fim}"
