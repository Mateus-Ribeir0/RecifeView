from dataclasses import dataclass

from app.domain.erros import ContribuicaoInvalida


@dataclass(frozen=True)
class ServicoDoFormulario:
    codigo: str
    rotulo: str
    categoria: str
    nome_na_fonte: str


@dataclass(frozen=True)
class TemaDoFormulario:
    chave: str
    rotulo: str
    servicos: tuple[ServicoDoFormulario, ...]


# Códigos, categorias e nomes iguais aos da Central 156, para o relato cair no mesmo vocabulário.
TEMAS_DO_FORMULARIO: tuple[TemaDoFormulario, ...] = (
    TemaDoFormulario(
        "iluminacao",
        "Iluminação",
        (
            ServicoDoFormulario(
                "55", "Lâmpada apagada", "ILUMINACAO PUBLICA", "MANUTENCAO EM LAMPADA APAGADA"
            ),
            ServicoDoFormulario(
                "51", "Trecho inteiro sem luz", "ILUMINACAO PUBLICA", "ACENDER CIRCUITO"
            ),
            ServicoDoFormulario(
                "47", "Lâmpada acesa de dia", "ILUMINACAO PUBLICA", "APAGAR LAMPADA"
            ),
        ),
    ),
    TemaDoFormulario(
        "limpeza",
        "Limpeza e coleta",
        (
            ServicoDoFormulario("6", "Entulho na rua", "LIMPEZA URBANA", "REMOCAO DE ENTULHOS"),
            ServicoDoFormulario(
                "80", "Mato em rua calçada", "LIMPEZA URBANA", "CAPINACAO EM VIA PAVIMENTADA"
            ),
            ServicoDoFormulario(
                "214", "Mato em rua de barro", "LIMPEZA URBANA", "CAPINACAO EM VIA NAO PAVIMENTADA"
            ),
            ServicoDoFormulario(
                "100", "Coleta de lixo irregular", "COLETA URBANA", "REGULARIZAR COLETA DOMICILIAR"
            ),
        ),
    ),
    TemaDoFormulario(
        "arvores",
        "Árvores",
        (
            ServicoDoFormulario("20", "Poda de árvore", "ARBORIZACAO", "PODA DE ARVORES"),
            ServicoDoFormulario(
                "35", "Árvore com risco de cair", "ARBORIZACAO", "VISTORIA DE ARVORES"
            ),
        ),
    ),
    TemaDoFormulario(
        "drenagem",
        "Drenagem e canais",
        (
            ServicoDoFormulario(
                "8", "Galeria ou valeta entupida", "DRENAGEM", "LIMPEZA DE GALERIAS E VALETAS"
            ),
            ServicoDoFormulario(
                "41",
                "Tampa de poço ou galeria faltando",
                "DRENAGEM",
                "REPOSICAO TAMPA DE POCO, GALERIAS,MEIO FIO E PRE-MOLDADOS",
            ),
            ServicoDoFormulario(
                "141", "Afundamento sobre galeria", "DRENAGEM", "RECUP. DE ABATIMENTO GALERIA"
            ),
            ServicoDoFormulario(
                "26", "Canal sujo ou entupido", "MACRODRENAGEM", "LIMPEZA DE CANAL"
            ),
        ),
    ),
    TemaDoFormulario(
        "ruas",
        "Ruas e calçadas",
        (
            ServicoDoFormulario("131", "Buraco na rua", "PAVIMENTACAO", "OPERACAO TAPA-BURACO"),
            ServicoDoFormulario(
                "144",
                "Paralelepípedo solto",
                "PAVIMENTACAO",
                "RECUPERACAO DE PAVIMENTO PARALELEPIPEDO",
            ),
            ServicoDoFormulario(
                "155",
                "Calçada quebrada",
                "MANUT. URBANA",
                "RECUPERACAO E MANUTENCAO DAS CALCADAS PUBLICAS DO RECIFE",
            ),
            ServicoDoFormulario(
                "116",
                "Escadaria danificada",
                "ESCADARIA",
                "MANUTENCAO RECUPERACAO DE ESCADARIA, CANALETA E CORRIMAO",
            ),
        ),
    ),
)

SERVICOS_POR_CODIGO = {
    servico.codigo: servico for tema in TEMAS_DO_FORMULARIO for servico in tema.servicos
}


def localizar_servico(codigo: str) -> ServicoDoFormulario:
    servico = SERVICOS_POR_CODIGO.get(codigo)
    if servico is None:
        raise ContribuicaoInvalida("servico", "Escolha um dos serviços da lista.")
    return servico
