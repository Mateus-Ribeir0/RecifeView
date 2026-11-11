from dataclasses import dataclass, field
from uuid import UUID

from app.application.casos_de_uso.encaminhamentos.servicos import (
    ServicosDeEncaminhamento,
    gerar_token_de_retorno,
)
from app.application.portas.encaminhamentos import NovoEncaminhamento
from app.domain.encaminhamento.encaminhamento import (
    TAMANHO_MAXIMO_DA_OBSERVACAO,
    CanalDeEnvio,
    Encaminhamento,
    OcorrenciaEncaminhavel,
    calcular_prazo_de_resposta,
    limpar_texto_curto,
    tem_encaminhamento_aberto,
)
from app.domain.encaminhamento.orgaos import CATALOGO_DE_ORGAOS, Orgao
from app.domain.encaminhamento.sugestao import SugestaoDeDestino
from app.domain.erros import OcorrenciaJaEncaminhada, OcorrenciaNaoEncontrada


@dataclass(frozen=True)
class OcorrenciaParaEncaminhar:
    ocorrencia: OcorrenciaEncaminhavel
    sugestao: SugestaoDeDestino
    encaminhamentos: list[Encaminhamento]
    canais: dict[Orgao, CanalDeEnvio] = field(default_factory=dict)

    @property
    def pode_encaminhar(self) -> bool:
        return not tem_encaminhamento_aberto(self.encaminhamentos)


@dataclass(frozen=True)
class PrepararEncaminhamento:
    servicos: ServicosDeEncaminhamento

    def executar(self, chave_registro: int) -> OcorrenciaParaEncaminhar:
        ocorrencia = self.servicos.encaminhamentos.ocorrencia(chave_registro)
        if ocorrencia is None:
            raise OcorrenciaNaoEncontrada
        canais = {
            dados.orgao: self.servicos.despacho.canal_de(dados.orgao)
            for dados in CATALOGO_DE_ORGAOS
        }
        return OcorrenciaParaEncaminhar(
            ocorrencia,
            self.servicos.sugerir(ocorrencia),
            self.servicos.encaminhamentos.da_ocorrencia(chave_registro),
            canais,
        )


@dataclass(frozen=True)
class PedidoDeEncaminhamento:
    chave_registro: int
    orgao: Orgao
    criado_por: UUID | None = None
    justificativa: str | None = None
    nota: float | None = None
    automatico: bool = False


@dataclass(frozen=True)
class EncaminharOcorrencia:
    servicos: ServicosDeEncaminhamento

    def executar(self, pedido: PedidoDeEncaminhamento) -> Encaminhamento:
        preparo = PrepararEncaminhamento(self.servicos).executar(pedido.chave_registro)
        if not preparo.pode_encaminhar:
            raise OcorrenciaJaEncaminhada
        justificativa = limpar_texto_curto(
            "justificativa", pedido.justificativa, TAMANHO_MAXIMO_DA_OBSERVACAO
        )
        agora = self.servicos.relogio.agora()
        token = gerar_token_de_retorno(agora)
        criado = self.servicos.encaminhamentos.criar(
            NovoEncaminhamento(
                ocorrencia=preparo.ocorrencia,
                orgao=pedido.orgao,
                orgao_sugerido=preparo.sugestao.orgao,
                canal=preparo.canais[pedido.orgao],
                criado_em=agora,
                prazo_de_resposta=calcular_prazo_de_resposta(agora.date()),
                token=token.guardado,
                criado_por=pedido.criado_por,
                nota=pedido.nota,
                justificativa=justificativa,
                automatico=pedido.automatico,
            )
        )
        return self.servicos.despachar(criado, token)
