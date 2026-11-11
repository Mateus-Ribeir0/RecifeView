import secrets
from dataclasses import dataclass
from datetime import datetime

from app.application.portas.encaminhamentos import (
    DespachoAosOrgaos,
    EncaminhamentoRepository,
    EnvioAoOrgaoFalhou,
    MudancaDeSituacao,
    TokenDeRetorno,
)
from app.application.portas.relogio import Relogio
from app.application.sessoes import calcular_hash_do_token
from app.domain.encaminhamento.encaminhamento import (
    VALIDADE_DO_LINK_DE_RETORNO,
    AutorDoEvento,
    Encaminhamento,
    OcorrenciaEncaminhavel,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.mensagem import montar_mensagem
from app.domain.encaminhamento.sugestao import SugestaoDeDestino, sugerir_destino, tema_na_camara
from app.domain.erros import EncaminhamentoNaoEncontrado

BYTES_DO_TOKEN_DE_RETORNO = 32
CAMINHO_DO_RETORNO = "/retorno/"
CANAL_NAO_RESPONDEU = "O canal do órgão não aceitou a mensagem. Confira a configuração e reenvie."


@dataclass(frozen=True)
class TokenGerado:
    valor: str
    guardado: TokenDeRetorno


def gerar_token_de_retorno(agora: datetime) -> TokenGerado:
    valor = secrets.token_urlsafe(BYTES_DO_TOKEN_DE_RETORNO)
    guardado = TokenDeRetorno(calcular_hash_do_token(valor), agora + VALIDADE_DO_LINK_DE_RETORNO)
    return TokenGerado(valor, guardado)


@dataclass(frozen=True)
class ServicosDeEncaminhamento:
    encaminhamentos: EncaminhamentoRepository
    despacho: DespachoAosOrgaos
    relogio: Relogio
    endereco_do_site: str

    def obter(self, encaminhamento_id: int) -> Encaminhamento:
        encaminhamento = self.encaminhamentos.buscar(encaminhamento_id)
        if encaminhamento is None:
            raise EncaminhamentoNaoEncontrado
        return encaminhamento

    def sugerir(self, ocorrencia: OcorrenciaEncaminhavel) -> SugestaoDeDestino:
        tema = tema_na_camara(ocorrencia.categoria)
        citacoes = self.encaminhamentos.citacoes_do_tema(tema) if tema else None
        return sugerir_destino(ocorrencia.orgao, citacoes)

    def despachar(self, encaminhamento: Encaminhamento, token: TokenGerado) -> Encaminhamento:
        """A falha do canal não desfaz o encaminhamento: ele fica gravado para reenvio."""
        link = f"{self.endereco_do_site.rstrip('/')}{CAMINHO_DO_RETORNO}{token.valor}"
        validade = token.guardado.expira_em.date()
        try:
            self.despacho.enviar(montar_mensagem(encaminhamento, link, validade))
        except EnvioAoOrgaoFalhou:
            falha = MudancaDeSituacao(
                SituacaoDoEncaminhamento.FALHOU,
                AutorDoEvento.SISTEMA,
                self.relogio.agora(),
                observacao=CANAL_NAO_RESPONDEU,
            )
            self.encaminhamentos.mudar_situacao(encaminhamento.id, falha)
        return self.obter(encaminhamento.id)
