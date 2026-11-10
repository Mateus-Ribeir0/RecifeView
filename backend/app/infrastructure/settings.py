from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

TAMANHO_MINIMO_DO_SEGREDO_JWT = 32
PASTA_PADRAO_DAS_IMPORTACOES = Path("../data/importacoes")
PASTA_PADRAO_DOS_EMAILS = Path("../data/emails")
BYTES_POR_MEGABYTE = 1024 * 1024


class ConfiguracaoDoBanco(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    url_do_banco: str


class Configuracao(ConfiguracaoDoBanco):
    segredo_jwt: SecretStr
    minutos_do_token_de_acesso: int = Field(default=15, gt=0)
    horas_da_sessao: int = Field(default=12, gt=0)
    cookie_seguro: bool = True
    origens_permitidas: list[str] = Field(default_factory=list)
    pasta_das_importacoes: Path = PASTA_PADRAO_DAS_IMPORTACOES
    tamanho_maximo_da_importacao_mb: int = Field(default=800, gt=0)
    sal_do_id_local: SecretStr | None = None
    pasta_dos_emails: Path = PASTA_PADRAO_DOS_EMAILS

    @field_validator("segredo_jwt")
    @classmethod
    def _exigir_segredo_longo(cls, segredo: SecretStr) -> SecretStr:
        if len(segredo.get_secret_value()) < TAMANHO_MINIMO_DO_SEGREDO_JWT:
            raise ValueError(
                f"API_SEGREDO_JWT precisa de {TAMANHO_MINIMO_DO_SEGREDO_JWT} caracteres"
            )
        return segredo

    @field_validator("sal_do_id_local")
    @classmethod
    def _ignorar_sal_vazio(cls, sal: SecretStr | None) -> SecretStr | None:
        return sal if sal and sal.get_secret_value() else None

    @property
    def limite_da_importacao_em_bytes(self) -> int:
        return self.tamanho_maximo_da_importacao_mb * BYTES_POR_MEGABYTE


def carregar_configuracao() -> Configuracao:
    return Configuracao()


def carregar_configuracao_do_banco() -> ConfiguracaoDoBanco:
    return ConfiguracaoDoBanco()
