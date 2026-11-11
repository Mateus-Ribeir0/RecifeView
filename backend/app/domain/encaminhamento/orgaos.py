from dataclasses import dataclass
from enum import StrEnum


class Orgao(StrEnum):
    EMLURB = "EMLURB"
    COMPESA = "COMPESA"
    NEOENERGIA = "NEOENERGIA"
    CTTU = "CTTU"
    DEFESA_CIVIL = "DEFESA_CIVIL"
    SEINFRA = "SEINFRA"
    URB = "URB"
    SAUDE = "SAUDE"
    MEIO_AMBIENTE = "MEIO_AMBIENTE"
    ORDEM_PUBLICA = "ORDEM_PUBLICA"


@dataclass(frozen=True)
class DadosDoOrgao:
    orgao: Orgao
    nome: str
    fora_da_prefeitura: bool


# Os mesmos órgãos que as indicações da Câmara citam, para a sugestão ter de onde vir.
CATALOGO_DE_ORGAOS: tuple[DadosDoOrgao, ...] = (
    DadosDoOrgao(Orgao.EMLURB, "Emlurb", fora_da_prefeitura=False),
    DadosDoOrgao(Orgao.COMPESA, "Compesa", fora_da_prefeitura=True),
    DadosDoOrgao(Orgao.NEOENERGIA, "Neoenergia Pernambuco", fora_da_prefeitura=True),
    DadosDoOrgao(Orgao.CTTU, "CTTU", fora_da_prefeitura=False),
    DadosDoOrgao(Orgao.DEFESA_CIVIL, "Defesa Civil do Recife", fora_da_prefeitura=False),
    DadosDoOrgao(Orgao.SEINFRA, "Secretaria de Infraestrutura", fora_da_prefeitura=False),
    DadosDoOrgao(Orgao.URB, "URB Recife", fora_da_prefeitura=False),
    DadosDoOrgao(Orgao.SAUDE, "Secretaria de Saúde", fora_da_prefeitura=False),
    DadosDoOrgao(Orgao.MEIO_AMBIENTE, "Secretaria de Meio Ambiente", fora_da_prefeitura=False),
    DadosDoOrgao(Orgao.ORDEM_PUBLICA, "Secretaria de Ordem Pública", fora_da_prefeitura=False),
)
DADOS_POR_ORGAO = {dados.orgao: dados for dados in CATALOGO_DE_ORGAOS}

NOMES_NA_FONTE: dict[str, Orgao] = {
    "EMLURB": Orgao.EMLURB,
    "COMPESA": Orgao.COMPESA,
    "NEOENERGIA": Orgao.NEOENERGIA,
    "CTTU": Orgao.CTTU,
    "SEDEC": Orgao.DEFESA_CIVIL,
    "SEDEC/DEFESA CIVIL": Orgao.DEFESA_CIVIL,
    "SECRETARIA EXECUTIVA DE DEFESA CIVIL": Orgao.DEFESA_CIVIL,
    "SEINFRA/INFRAESTRUTURA": Orgao.SEINFRA,
    "URB": Orgao.URB,
    "SAUDE": Orgao.SAUDE,
    "SECRETARIA DE SAUDE": Orgao.SAUDE,
    "MEIO AMBIENTE": Orgao.MEIO_AMBIENTE,
    "SECRETARIA DE MEIO AMBIENTE E SUSTENTABILIDADE": Orgao.MEIO_AMBIENTE,
    "ORDEM PUBLICA/SEOPS": Orgao.ORDEM_PUBLICA,
    "SECRETARIA DE ORDEM PUBLICA E SEGURANCA": Orgao.ORDEM_PUBLICA,
}


def orgao_da_fonte(nome: str | None) -> Orgao | None:
    if nome is None:
        return None
    return NOMES_NA_FONTE.get(nome.strip().upper())


def nome_do_orgao(orgao: Orgao) -> str:
    return DADOS_POR_ORGAO[orgao].nome
