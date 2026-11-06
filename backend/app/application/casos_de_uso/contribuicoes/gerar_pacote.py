import csv
import io
from dataclasses import dataclass
from uuid import UUID

from app.application.casos_de_uso.contribuicoes.expurgar_enderecos import ExpurgarEnderecos
from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.casos_de_uso.importacoes.analisar_arquivo import AnalisarArquivo
from app.application.casos_de_uso.importacoes.definir_colunas import (
    DefinirColunas,
    EscolhaDeColunas,
)
from app.application.portas.contribuicoes import OcorrenciaDoPacote
from app.application.portas.importacoes import ArquivoRecebido, NovaImportacao
from app.domain.erros import PacoteVazio, PenteFinoPendente
from app.domain.fontes import Fonte
from app.domain.importacao.importacao import Importacao, StatusDaImportacao

COLUNAS_DO_PACOTE = (
    "CONTRIBUICAO_ID",
    "DATA_ABERTURA",
    "CATEGORIA",
    "SERVICO_CODIGO",
    "SERVICO",
    "BAIRRO_OFICIAL",
    "ID_LOCAL",
    "NUMERO_INFORMADO",
    "RELATOS_SOMADOS",
)


def montar_csv_do_pacote(ocorrencias: list[OcorrenciaDoPacote]) -> bytes:
    """O pacote não leva endereço nem texto: só o que a base analítica pode guardar."""
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";")
    escritor.writerow(COLUNAS_DO_PACOTE)
    for item in ocorrencias:
        escritor.writerow(
            (
                item.contribuicao_id,
                item.data_relato.isoformat(),
                item.categoria,
                item.servico_codigo,
                item.servico,
                item.bairro_oficial,
                item.id_local or "",
                "SIM" if item.numero_informado else "NAO",
                item.relatos,
            )
        )
    return saida.getvalue().encode()


@dataclass(frozen=True)
class GerarPacote:
    """Junta as ocorrências revisadas e entrega ao fluxo normal de importação."""

    servicos: ServicosDeContribuicoes

    def executar(self, usuario_id: UUID) -> Importacao:
        contribuicoes = self.servicos.contribuicoes
        ExpurgarEnderecos(contribuicoes, self.servicos.relogio).executar()
        if contribuicoes.contar_pares_abertos() > 0:
            raise PenteFinoPendente
        ocorrencias = contribuicoes.prontas_para_pacote()
        if not ocorrencias:
            raise PacoteVazio
        importacao = self.servicos.importacao.importacoes.criar(
            NovaImportacao(self._gravar(ocorrencias), usuario_id), StatusDaImportacao.ANALISANDO
        )
        contribuicoes.marcar_no_pacote(
            [item.contribuicao_id for item in ocorrencias], importacao.id
        )
        self.servicos.importacao.fila.enfileirar(lambda: self._preparar(importacao.id))
        return importacao

    def _gravar(self, ocorrencias: list[OcorrenciaDoPacote]) -> ArquivoRecebido:
        hoje = self.servicos.relogio.agora().date().isoformat()
        recebimento = self.servicos.importacao.armazenamento.iniciar_recebimento(
            f"pacote_formulario_{hoje}.csv"
        )
        recebimento.gravar(montar_csv_do_pacote(ocorrencias))
        return recebimento.concluir()

    def _preparar(self, importacao_id: int) -> None:
        """As colunas do pacote são sempre as mesmas: a pessoa começa nas decisões."""
        servicos = self.servicos.importacao
        AnalisarArquivo(servicos).executar(importacao_id)
        importacao = servicos.obter(importacao_id)
        if importacao.status is not StatusDaImportacao.AGUARDANDO_COLUNAS:
            return
        escolha = EscolhaDeColunas(
            Fonte.FORMULARIO,
            self.servicos.relogio.agora().date(),
            dict(importacao.decisoes.mapeamento),
            dict(importacao.decisoes.valores_fixos),
        )
        DefinirColunas(servicos).executar(importacao_id, escolha)
