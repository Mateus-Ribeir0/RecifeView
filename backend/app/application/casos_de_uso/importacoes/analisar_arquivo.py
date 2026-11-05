from dataclasses import asdict, dataclass, replace
from itertools import islice
from typing import Any

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import TabelaDoArquivo
from app.domain.erros import ArquivoIlegivel, ArquivoVazio
from app.domain.importacao.decisoes import Decisoes
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.domain.importacao.layouts import Layout, reconhecer_layout
from app.domain.importacao.mapeamento import OrigemDaSugestao, SugestaoDeColuna, sugerir_mapeamento
from app.domain.importacao.privacidade import (
    ROTULOS_DOS_MOTIVOS,
    localizar_colunas_bloqueadas,
    motivo_pelo_conteudo,
)

LINHAS_DA_AMOSTRA = 2000
EXEMPLOS_POR_COLUNA = 3
TAMANHO_MAXIMO_DO_EXEMPLO = 60


def _exemplos_da_coluna(amostra: list[list[str]], indice: int) -> list[str]:
    exemplos: list[str] = []
    for linha in amostra:
        valor = linha[indice].strip() if indice < len(linha) else ""
        if not valor or valor in exemplos or motivo_pelo_conteudo(valor) is not None:
            continue
        exemplos.append(valor[:TAMANHO_MAXIMO_DO_EXEMPLO])
        if len(exemplos) == EXEMPLOS_POR_COLUNA:
            break
    return exemplos


def _descrever_colunas(
    sugestoes: list[SugestaoDeColuna], amostra: list[list[str]]
) -> list[dict[str, Any]]:
    descritas = []
    for indice, sugestao in enumerate(sugestoes):
        motivo = sugestao.motivo_de_bloqueio
        descritas.append(
            {
                "nome": sugestao.coluna,
                "campo": sugestao.campo,
                "origem": sugestao.origem.value,
                "bloqueada": motivo is not None,
                "motivo_de_bloqueio": ROTULOS_DOS_MOTIVOS[motivo] if motivo else None,
                "exemplos": [] if motivo else _exemplos_da_coluna(amostra, indice),
            }
        )
    return descritas


@dataclass(frozen=True)
class AnalisarArquivo:
    """Lê a estrutura do arquivo, reconhece a fonte e sugere o mapeamento das colunas."""

    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int) -> None:
        importacao = self.servicos.obter(importacao_id)
        try:
            self._analisar(importacao)
        except (ArquivoIlegivel, ArquivoVazio) as erro:
            self._registrar_falha(importacao, erro)

    def _analisar(self, importacao: Importacao) -> None:
        tabela = self.servicos.abrir_tabela(importacao)
        amostra = list(islice(tabela.linhas(), LINHAS_DA_AMOSTRA))
        if not tabela.colunas or not amostra:
            raise ArquivoVazio
        layout = reconhecer_layout(tabela.colunas)
        bloqueadas = localizar_colunas_bloqueadas(tabela.colunas, amostra)
        sugestoes = sugerir_mapeamento(tabela.colunas, layout, bloqueadas)
        estrutura = self._montar_estrutura(importacao, tabela, sugestoes, amostra)
        estrutura["layout_nome"] = layout.nome
        estrutura["guardar_arquivo"] = not bloqueadas
        estrutura["colunas_bloqueadas"] = [asdict(_bloqueio) for _bloqueio in bloqueadas]
        self.servicos.importacoes.salvar(
            replace(
                importacao,
                status=StatusDaImportacao.AGUARDANDO_COLUNAS,
                progresso=0,
                layout=layout.codigo.value,
                fonte=layout.fonte.value if layout.fonte else None,
                estrutura=estrutura,
                decisoes=self._decisoes_iniciais(importacao, layout, sugestoes),
            )
        )

    def _montar_estrutura(
        self,
        importacao: Importacao,
        tabela: TabelaDoArquivo,
        sugestoes: list[SugestaoDeColuna],
        amostra: list[list[str]],
    ) -> dict[str, Any]:
        repetidas = self.servicos.importacoes.mesmo_arquivo(
            importacao.hash_do_arquivo, importacao.id
        )
        return {
            **importacao.estrutura,
            "formato": tabela.formato,
            "codificacao": tabela.codificacao,
            "separador": tabela.separador,
            "colunas": _descrever_colunas(sugestoes, amostra),
            "mesmo_arquivo": [
                {
                    "id": anterior.id,
                    "criada_em": anterior.criada_em.isoformat(),
                    "status": anterior.status.value,
                }
                for anterior in repetidas
            ],
        }

    def _decisoes_iniciais(
        self, importacao: Importacao, layout: Layout, sugestoes: list[SugestaoDeColuna]
    ) -> Decisoes:
        return Decisoes(
            fonte=layout.fonte,
            data_do_retrato=self.servicos.relogio.agora().date(),
            mapeamento={s.coluna: s.campo for s in sugestoes if s.campo is not None},
            valores_fixos=dict(layout.valores_fixos),
        )

    def _registrar_falha(self, importacao: Importacao, erro: Exception) -> None:
        mensagem = (
            "O arquivo está vazio ou não tem linhas de dados."
            if isinstance(erro, ArquivoVazio)
            else "Não foi possível ler o arquivo. Confira o formato e tente de novo."
        )
        self.servicos.importacoes.salvar(
            replace(importacao, status=StatusDaImportacao.FALHOU, mensagem_de_erro=mensagem)
        )


def colunas_com_uso_fixo(importacao: Importacao) -> dict[str, str | None]:
    """Colunas bloqueadas não aceitam outro destino: só o uso interno que a análise definiu."""
    colunas: list[dict[str, Any]] = importacao.estrutura.get("colunas", [])
    return {
        coluna["nome"]: coluna["campo"]
        for coluna in colunas
        if coluna["origem"] == OrigemDaSugestao.BLOQUEADA.value
    }
