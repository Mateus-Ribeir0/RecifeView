from dataclasses import dataclass, field

from app.application.casos_de_uso.corporativo.servicos import ServicosDoOrgao, orgao_da_conta
from app.application.casos_de_uso.encaminhamentos.retorno import (
    QuemResponde,
    RespostaAoEncaminhamento,
    validar_resposta,
)
from app.application.portas.encaminhamentos import MudancaDeSituacao
from app.domain.encaminhamento.encaminhamento import (
    AutorDoEvento,
    Encaminhamento,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.mesmo_problema import encontrar_mesmo_problema
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import EncaminhamentoInvalido
from app.domain.usuario import Usuario

MAXIMO_DE_OCORRENCIAS_JUNTAS = 20
EXPLICACOES_OBRIGATORIAS = {
    SituacaoDoEncaminhamento.RESOLVIDO: "Conte ao cidadão o que foi feito.",
    SituacaoDoEncaminhamento.DEVOLVIDO: "Explique ao cidadão por que a ocorrência não é do órgão.",
}


@dataclass(frozen=True)
class RespostaDoOrgao:
    encaminhamento_id: int
    resposta: RespostaAoEncaminhamento
    tambem: tuple[int, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RespostaRegistrada:
    principal: Encaminhamento
    demais: list[Encaminhamento]


def _exigir_explicacao(resposta: RespostaAoEncaminhamento) -> None:
    motivo = EXPLICACOES_OBRIGATORIAS.get(resposta.situacao)
    if motivo and not (resposta.resposta_ao_cidadao or "").strip():
        raise EncaminhamentoInvalido("resposta_ao_cidadao", motivo)


@dataclass(frozen=True)
class ResponderComoOrgao:
    """Valida todas antes de gravar a primeira: a resposta em grupo é tudo ou nada."""

    servicos: ServicosDoOrgao

    def executar(self, usuario: Usuario, pedido: RespostaDoOrgao) -> RespostaRegistrada:
        orgao = orgao_da_conta(usuario)
        _exigir_explicacao(pedido.resposta)
        principal = self.servicos.do_orgao(pedido.encaminhamento_id, orgao)
        alvos = [principal, *self._juntas(principal, pedido.tambem, orgao)]
        quem = QuemResponde(AutorDoEvento.ORGAO, usuario.id)
        servicos = self.servicos.encaminhamentos
        mudancas = [
            (item, validar_resposta(servicos, item, pedido.resposta, quem)) for item in alvos
        ]
        registrados = [self._gravar(item, mudanca) for item, mudanca in mudancas]
        return RespostaRegistrada(registrados[0], registrados[1:])

    def _juntas(
        self, principal: Encaminhamento, tambem: tuple[int, ...], orgao: Orgao
    ) -> list[Encaminhamento]:
        escolhidos = [item for item in dict.fromkeys(tambem) if item != principal.id]
        if not escolhidos:
            return []
        if len(escolhidos) > MAXIMO_DE_OCORRENCIAS_JUNTAS:
            raise EncaminhamentoInvalido("tambem", "Escolha até 20 ocorrências por vez.")
        repositorio = self.servicos.encaminhamentos.encaminhamentos
        parecidos = encontrar_mesmo_problema(
            principal.ocorrencia, repositorio.comparaveis([principal.ocorrencia])
        )
        do_mesmo_problema = {item.encaminhamento.id for item in parecidos}
        if not set(escolhidos) <= do_mesmo_problema:
            raise EncaminhamentoInvalido(
                "tambem", "Só dá para juntar ocorrências do mesmo problema."
            )
        return [self.servicos.do_orgao(item, orgao) for item in escolhidos]

    def _gravar(self, encaminhamento: Encaminhamento, mudanca: MudancaDeSituacao) -> Encaminhamento:
        servicos = self.servicos.encaminhamentos
        servicos.encaminhamentos.mudar_situacao(encaminhamento.id, mudanca)
        respondido = servicos.obter(encaminhamento.id)
        servicos.avisos.avisar(respondido, AutorDoEvento.ORGAO)
        return respondido
