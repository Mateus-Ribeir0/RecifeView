from enum import StrEnum


class Fonte(StrEnum):
    CENTRAL_156 = "156_EMLURB"
    DEFESA_CIVIL = "DEFESA_CIVIL"
    OUVIDORIA = "OUVIDORIA"
    SEDEC = "SEDEC_CHAMADOS"
    CAMARA = "CAMARA_REQUERIMENTOS"


class Iniciativa(StrEnum):
    CIDADAO = "CIDADAO"
    PROATIVA = "PROATIVA"
    VEREADOR = "VEREADOR"
    INDEFINIDA = "INDEFINIDA"


ROTULOS_DAS_FONTES = {
    Fonte.CENTRAL_156: "Central 156 / Emlurb",
    Fonte.DEFESA_CIVIL: "Defesa Civil",
    Fonte.OUVIDORIA: "Ouvidoria",
    Fonte.SEDEC: "SEDEC, áreas de risco",
    Fonte.CAMARA: "Câmara Municipal",
}
