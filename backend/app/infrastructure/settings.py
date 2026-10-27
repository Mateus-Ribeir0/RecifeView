from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

TAMANHO_MINIMO_DO_SEGREDO_JWT = 32


class ConfiguracaoDoBanco(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    url_do_banco: str


class Configuracao(ConfiguracaoDoBanco):
    segredo_jwt: SecretStr
    minutos_do_token_de_acesso: int = Field(default=15, gt=0)
    horas_da_sessao: int = Field(default=12, gt=0)
    cookie_seguro: bool = True
    origens_permitidas: list[str] = Field(default_factory=list)

    @field_validator("segredo_jwt")
    @classmethod
    def _exigir_segredo_longo(cls, segredo: SecretStr) -> SecretStr:
        if len(segredo.get_secret_value()) < TAMANHO_MINIMO_DO_SEGREDO_JWT:
            raise ValueError(
                f"API_SEGREDO_JWT precisa de {TAMANHO_MINIMO_DO_SEGREDO_JWT} caracteres"
            )
        return segredo


def carregar_configuracao() -> Configuracao:
    return Configuracao()


def carregar_configuracao_do_banco() -> ConfiguracaoDoBanco:
    return ConfiguracaoDoBanco()
