from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.domain.encaminhamento.encaminhamento import CanalDeEnvio
from app.domain.encaminhamento.orgaos import Orgao
from app.infrastructure.email.envio_por_smtp import SegurancaDoSmtp, ServidorSmtp

TAMANHO_MINIMO_DO_SEGREDO_JWT = 32
PASTA_PADRAO_DAS_IMPORTACOES = Path("../data/importacoes")
PASTA_PADRAO_DOS_EMAILS = Path("../data/emails")
PASTA_PADRAO_DOS_ENCAMINHAMENTOS = Path("../data/encaminhamentos")
ENDERECO_PADRAO_DO_SITE = "http://localhost:5173"
HOSTS_PADRAO_DE_IMPORTACAO = ["dados.recife.pe.gov.br"]
SEGUNDOS_PADRAO_DA_EXTRACAO = 120
ESQUEMA_ACEITO_DOS_BANCOS = "postgresql"
INICIOS_ACEITOS_DO_WEBHOOK = ("https://", "http://localhost", "http://127.0.0.1")
BYTES_POR_MEGABYTE = 1024 * 1024
PORTA_PADRAO_DO_SMTP = 587


class CanalConfigurado(BaseModel):
    canal: CanalDeEnvio
    destino: str = ""
    token: SecretStr | None = None

    @model_validator(mode="after")
    def _exigir_destino_do_canal(self) -> Self:
        if self.canal is CanalDeEnvio.EMAIL and "@" not in self.destino:
            raise ValueError("O canal de e-mail precisa de um endereço em destino")
        if self.canal is CanalDeEnvio.WEBHOOK and not self.destino.startswith(
            INICIOS_ACEITOS_DO_WEBHOOK
        ):
            raise ValueError("O webhook precisa de um endereço https em destino")
        return self


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
    smtp_servidor: str | None = None
    smtp_porta: int = Field(default=PORTA_PADRAO_DO_SMTP, gt=0)
    smtp_seguranca: SegurancaDoSmtp = SegurancaDoSmtp.STARTTLS
    smtp_usuario: str | None = None
    smtp_senha: SecretStr | None = None
    smtp_remetente: str | None = None
    canais_dos_orgaos: dict[Orgao, CanalConfigurado] = Field(default_factory=dict)
    pasta_dos_encaminhamentos: Path = PASTA_PADRAO_DOS_ENCAMINHAMENTOS
    endereco_do_site: str = ENDERECO_PADRAO_DO_SITE
    hosts_de_importacao: list[str] = Field(default_factory=lambda: list(HOSTS_PADRAO_DE_IMPORTACAO))
    bancos_de_origem: dict[str, SecretStr] = Field(default_factory=dict)
    segundos_da_extracao: int = Field(default=SEGUNDOS_PADRAO_DA_EXTRACAO, gt=0)

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

    @field_validator("bancos_de_origem")
    @classmethod
    def _aceitar_so_postgresql(cls, bancos: dict[str, SecretStr]) -> dict[str, SecretStr]:
        for nome, url in bancos.items():
            if not url.get_secret_value().startswith(ESQUEMA_ACEITO_DOS_BANCOS):
                raise ValueError(f"API_BANCOS_DE_ORIGEM: {nome} precisa ser um PostgreSQL")
        return bancos

    @field_validator("smtp_servidor", "smtp_usuario", "smtp_senha", "smtp_remetente", mode="before")
    @classmethod
    def _ignorar_texto_vazio(cls, valor: object) -> object:
        return None if valor == "" else valor

    @model_validator(mode="after")
    def _exigir_remetente_do_smtp(self) -> Self:
        if self.smtp_servidor and not (self.smtp_remetente or self.smtp_usuario):
            raise ValueError(
                "Com API_SMTP_SERVIDOR, informe API_SMTP_REMETENTE ou API_SMTP_USUARIO"
            )
        return self

    @property
    def servidor_smtp(self) -> ServidorSmtp | None:
        remetente = self.smtp_remetente or self.smtp_usuario
        if self.smtp_servidor is None or remetente is None:
            return None
        return ServidorSmtp(
            endereco=self.smtp_servidor,
            porta=self.smtp_porta,
            remetente=remetente,
            seguranca=self.smtp_seguranca,
            usuario=self.smtp_usuario,
            senha=self.smtp_senha,
        )

    @property
    def limite_da_importacao_em_bytes(self) -> int:
        return self.tamanho_maximo_da_importacao_mb * BYTES_POR_MEGABYTE


def carregar_configuracao() -> Configuracao:
    return Configuracao()


def carregar_configuracao_do_banco() -> ConfiguracaoDoBanco:
    return ConfiguracaoDoBanco()
