# Grafias das fontes e nomes populares para os bairros oficiais (build_dataset.py e N3, seção 1.6).
APELIDOS_DE_BAIRRO = {
    "COHAB IBURA DE CIMA": "COHAB",
    "COHAB - IBURA DE CIMA": "COHAB",
    "IBURA DE BAIXO": "IBURA",
    "SITIO DOS PINTOS": "SITIO DOS PINTOS - SAO BRAS",
    "SITIO DOS PINTOS SAO BRAS": "SITIO DOS PINTOS - SAO BRAS",
    "SAO BRAS": "SITIO DOS PINTOS - SAO BRAS",
    "ALTO DO MANDU SITIO GRANDE": "ALTO DO MANDU",
    "CGO. DO JENIPAPO": "CORREGO DO JENIPAPO",
    "BAIRRO DO RECIFE": "RECIFE",
    "RECIFE ANTIGO": "RECIFE",
    "JD. SAO PAULO": "JARDIM SAO PAULO",
    "POCO DA PANELA": "POCO",
    "ZUMBI DO PACHECO": "ZUMBI",
}

VALORES_SEM_BAIRRO = frozenset({"", "NAO INFORMADO", "NAO INFORMADA", "SEM BAIRRO", "N/I", "NI"})


def localizar_bairro(valor: str, oficiais: dict[str, str]) -> str | None:
    """Devolve o bairro oficial de um valor já normalizado, ou None se não houver."""
    if valor in oficiais:
        return valor
    apelido = APELIDOS_DE_BAIRRO.get(valor)
    return apelido if apelido in oficiais else None
