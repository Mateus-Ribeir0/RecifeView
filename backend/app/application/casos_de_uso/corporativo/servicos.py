from dataclasses import dataclass
from datetime import date

from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.portas.encaminhamentos import PessoasQueAcompanham
from app.application.portas.indicadores import (
    DemandaDoOrgaoRepository,
    IndicadoresDoCicloRepository,
)
from app.domain.encaminhamento.encaminhamento import Encaminhamento, SituacaoDoEncaminhamento
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import AcessoNegado, EncaminhamentoNaoEncontrado
from app.domain.usuario import Usuario

# O que falhou no envio volta para a gestão reenviar: o órgão nunca chegou a receber.
SITUACOES_VISIVEIS_AO_ORGAO = frozenset(
    {
        SituacaoDoEncaminhamento.ENVIADO,
        SituacaoDoEncaminhamento.RECEBIDO,
        SituacaoDoEncaminhamento.RESOLVIDO,
        SituacaoDoEncaminhamento.DEVOLVIDO,
    }
)


def orgao_da_conta(usuario: Usuario) -> Orgao:
    if not usuario.e_corporativo or usuario.orgao is None:
        raise AcessoNegado
    return usuario.orgao


@dataclass(frozen=True)
class ServicosDoOrgao:
    encaminhamentos: ServicosDeEncaminhamento
    indicadores: IndicadoresDoCicloRepository
    pessoas: PessoasQueAcompanham
    demanda: DemandaDoOrgaoRepository

    def hoje(self) -> date:
        return self.encaminhamentos.relogio.agora().date()

    def do_orgao(self, encaminhamento_id: int, orgao: Orgao) -> Encaminhamento:
        """Outro órgão recebe 404, e não 403: nem a existência do encaminhamento vaza."""
        encaminhamento = self.encaminhamentos.encaminhamentos.buscar(encaminhamento_id)
        if (
            encaminhamento is None
            or encaminhamento.orgao is not orgao
            or encaminhamento.situacao not in SITUACOES_VISIVEIS_AO_ORGAO
        ):
            raise EncaminhamentoNaoEncontrado
        return encaminhamento
