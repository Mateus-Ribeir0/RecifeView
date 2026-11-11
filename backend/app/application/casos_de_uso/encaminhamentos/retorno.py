from dataclasses import dataclass
from uuid import UUID

from app.application.casos_de_uso.encaminhamentos.servicos import (
    ServicosDeEncaminhamento,
    gerar_token_de_retorno,
)
from app.application.portas.encaminhamentos import MudancaDeSituacao
from app.application.sessoes import calcular_hash_do_token
from app.domain.encaminhamento.encaminhamento import (
    SITUACOES_DE_RETORNO,
    TAMANHO_MAXIMO_DA_OBSERVACAO,
    TAMANHO_MAXIMO_DO_PROTOCOLO_DO_ORGAO,
    AutorDoEvento,
    Encaminhamento,
    SituacaoDoEncaminhamento,
    exigir_transicao,
    limpar_texto_curto,
)
from app.domain.erros import LinkDeRetornoInvalido, TransicaoInvalida


@dataclass(frozen=True)
class RespostaAoEncaminhamento:
    situacao: SituacaoDoEncaminhamento
    protocolo_do_orgao: str | None = None
    observacao: str | None = None


@dataclass(frozen=True)
class QuemResponde:
    autor: AutorDoEvento
    usuario_id: UUID | None = None


def _mudanca_validada(
    servicos: ServicosDeEncaminhamento,
    encaminhamento: Encaminhamento,
    resposta: RespostaAoEncaminhamento,
    quem: QuemResponde,
) -> MudancaDeSituacao:
    if resposta.situacao not in SITUACOES_DE_RETORNO:
        raise TransicaoInvalida
    exigir_transicao(encaminhamento.situacao, resposta.situacao)
    return MudancaDeSituacao(
        situacao=resposta.situacao,
        autor=quem.autor,
        ocorrido_em=servicos.relogio.agora(),
        usuario_id=quem.usuario_id,
        observacao=limpar_texto_curto(
            "observacao", resposta.observacao, TAMANHO_MAXIMO_DA_OBSERVACAO
        ),
        protocolo_do_orgao=limpar_texto_curto(
            "protocolo_do_orgao", resposta.protocolo_do_orgao, TAMANHO_MAXIMO_DO_PROTOCOLO_DO_ORGAO
        ),
    )


@dataclass(frozen=True)
class AbrirPeloLink:
    servicos: ServicosDeEncaminhamento

    def executar(self, token: str) -> Encaminhamento:
        hash_do_token = calcular_hash_do_token(token)
        agora = self.servicos.relogio.agora()
        encaminhamento = self.servicos.encaminhamentos.buscar_pelo_token(hash_do_token, agora)
        if encaminhamento is None:
            raise LinkDeRetornoInvalido
        return encaminhamento


@dataclass(frozen=True)
class RegistrarRetornoPeloLink:
    servicos: ServicosDeEncaminhamento

    def executar(self, token: str, resposta: RespostaAoEncaminhamento) -> Encaminhamento:
        encaminhamento = AbrirPeloLink(self.servicos).executar(token)
        quem = QuemResponde(AutorDoEvento.ORGAO)
        mudanca = _mudanca_validada(self.servicos, encaminhamento, resposta, quem)
        self.servicos.encaminhamentos.mudar_situacao(encaminhamento.id, mudanca)
        return self.servicos.obter(encaminhamento.id)


@dataclass(frozen=True)
class RegistrarRetornoPelaGestao:
    servicos: ServicosDeEncaminhamento

    def executar(
        self, encaminhamento_id: int, resposta: RespostaAoEncaminhamento, usuario_id: UUID
    ) -> Encaminhamento:
        encaminhamento = self.servicos.obter(encaminhamento_id)
        quem = QuemResponde(AutorDoEvento.GESTAO, usuario_id)
        mudanca = _mudanca_validada(self.servicos, encaminhamento, resposta, quem)
        self.servicos.encaminhamentos.mudar_situacao(encaminhamento_id, mudanca)
        return self.servicos.obter(encaminhamento_id)


@dataclass(frozen=True)
class ReenviarEncaminhamento:
    """Só depois de uma falha do canal. Um link novo substitui o anterior."""

    servicos: ServicosDeEncaminhamento

    def executar(self, encaminhamento_id: int, usuario_id: UUID) -> Encaminhamento:
        encaminhamento = self.servicos.obter(encaminhamento_id)
        exigir_transicao(encaminhamento.situacao, SituacaoDoEncaminhamento.ENVIADO)
        agora = self.servicos.relogio.agora()
        token = gerar_token_de_retorno(agora)
        canal = self.servicos.despacho.canal_de(encaminhamento.orgao)
        self.servicos.encaminhamentos.preparar_reenvio(encaminhamento_id, token.guardado, canal)
        reenvio = MudancaDeSituacao(
            SituacaoDoEncaminhamento.ENVIADO, AutorDoEvento.GESTAO, agora, usuario_id
        )
        self.servicos.encaminhamentos.mudar_situacao(encaminhamento_id, reenvio)
        return self.servicos.despachar(self.servicos.obter(encaminhamento_id), token)
