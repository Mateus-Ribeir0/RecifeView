from datetime import date

import pytest

from app.domain.ahp import (
    JULGAMENTOS_PADRAO,
    IndicadoresDoBairro,
    calcular_pesos,
    indice_de_prioridade,
    matriz_de_comparacao,
    medir_sensibilidade,
    nota_de_atraso,
    nota_de_reincidencia,
    pares,
    posicoes_relativas,
    razao_de_consistencia,
)
from app.domain.erros import PeriodoInvalido
from app.domain.filtros import Filtros
from app.domain.prazos import minimo_de_pedidos_por_categoria
from app.domain.prioridade import (
    Ocorrencia,
    classificar_ocorrencias,
    classificar_so_pelo_atraso,
    distribuir_notas,
    sortear_amostra,
)
from app.domain.suavizacao import Ponto, suavizar
from app.domain.territorio import calcular_taxa, classe_da_taxa, limites_das_faixas


def bairro(nome: str, risco: float | None, atraso: float | None = 1.0) -> IndicadoresDoBairro:
    return IndicadoresDoBairro(nome, nome.title(), "1", risco, 10.0, atraso, 5.0)


def test_periodo_invertido_e_recusado() -> None:
    with pytest.raises(PeriodoInvalido):
        Filtros(2025, 2021)


def test_julgamentos_do_grupo_dao_os_pesos_publicados_na_n4() -> None:
    pesos = calcular_pesos(JULGAMENTOS_PADRAO)

    assert pesos["risco"] == pytest.approx(0.455, abs=0.001)
    assert pesos["vulnerabilidade"] == pytest.approx(0.263, abs=0.001)
    assert pesos["atraso"] == pytest.approx(0.141, abs=0.001)
    assert pesos["reincidencia"] == pytest.approx(0.141, abs=0.001)


def test_julgamentos_do_grupo_sao_coerentes() -> None:
    razao = razao_de_consistencia(matriz_de_comparacao(JULGAMENTOS_PADRAO))

    assert razao == pytest.approx(0.004, abs=0.001)


def test_julgamentos_contraditorios_passam_do_limite() -> None:
    julgamentos = dict.fromkeys(pares(), 1.0)
    julgamentos[("risco", "vulnerabilidade")] = 9.0
    julgamentos[("vulnerabilidade", "atraso")] = 9.0
    julgamentos[("risco", "atraso")] = 1 / 9

    assert razao_de_consistencia(matriz_de_comparacao(julgamentos)) > 0.10


def test_matriz_e_reciproca() -> None:
    matriz = matriz_de_comparacao(JULGAMENTOS_PADRAO)

    assert matriz[0][2] == 3.0
    assert matriz[2][0] == pytest.approx(1 / 3)


def test_posicao_relativa_divide_o_empate_e_zera_quem_nao_tem_dado() -> None:
    assert posicoes_relativas([10.0, 20.0, 20.0, None]) == pytest.approx([1 / 3, 5 / 6, 5 / 6, 0.0])


def test_indice_ordena_e_empata_na_mesma_posicao() -> None:
    bairros = [bairro("A", 1.0), bairro("B", 3.0), bairro("C", 3.0)]

    resultado = indice_de_prioridade(bairros, calcular_pesos(JULGAMENTOS_PADRAO))

    assert [item.indicadores.bairro_oficial for item in resultado][-1] == "A"
    assert [item.posicao for item in resultado] == [1, 1, 3]


def test_contribuicoes_somam_o_indice() -> None:
    resultado = indice_de_prioridade([bairro("A", 1.0)], calcular_pesos(JULGAMENTOS_PADRAO))

    assert sum(resultado[0].contribuicoes.values()) == pytest.approx(resultado[0].indice)


def test_sensibilidade_testa_quatro_fatores_por_criterio() -> None:
    bairros = [bairro(f"B{indice}", float(indice)) for indice in range(12)]

    testes = medir_sensibilidade(bairros, calcular_pesos(JULGAMENTOS_PADRAO))

    assert len(testes) == 16
    assert all(0 <= teste.mantidos_no_top <= 10 for teste in testes)


@pytest.mark.parametrize(
    ("idade", "prazo", "nota"),
    [(10, 10, 0.5), (20, 10, 1.0), (40, 10, 1.0), (0, 10, 0.0), (5, None, 0.0), (0, 0, 0.0)],
)
def test_nota_de_atraso(idade: int, prazo: float | None, nota: float) -> None:
    assert nota_de_atraso(idade, prazo) == pytest.approx(nota)


@pytest.mark.parametrize(
    ("anteriores", "nota"), [(None, 0.0), (0, 0.0), (1, 0.289), (10, 1.0), (50, 1.0)]
)
def test_nota_de_reincidencia(anteriores: int | None, nota: float) -> None:
    assert nota_de_reincidencia(anteriores) == pytest.approx(nota, abs=0.001)


def ocorrencia(bairro_oficial: str, idade: int) -> Ocorrencia:
    return Ocorrencia(
        date(2026, 1, 1),
        idade,
        prazo_tipico_dias=10.0,
        pedidos_anteriores=0,
        bairro_oficial=bairro_oficial,
    )


def test_fila_deixa_de_fora_bairro_sem_indice() -> None:
    pesos = calcular_pesos(JULGAMENTOS_PADRAO)

    fila = classificar_ocorrencias([ocorrencia("FORA", 5)], [bairro("A", 1.0)], pesos)

    assert fila == []


def test_fila_poe_o_mais_atrasado_primeiro() -> None:
    pesos = calcular_pesos(JULGAMENTOS_PADRAO)
    ocorrencias = [ocorrencia("A", 5), ocorrencia("A", 30)]

    fila = classificar_ocorrencias(ocorrencias, [bairro("A", 1.0)], pesos)

    assert [item.ocorrencia.idade_dias for item in fila] == [30, 5]
    assert [item.fila for item in fila] == [1, 2]


def test_ouvidoria_e_classificada_so_pelo_atraso() -> None:
    ocorrencias = [
        Ocorrencia(None, 0, dias_alem_do_prazo=10),
        Ocorrencia(None, 0, dias_alem_do_prazo=30),
    ]

    fila = classificar_so_pelo_atraso(ocorrencias)

    assert fila[0].ocorrencia.dias_alem_do_prazo == 30
    assert fila[0].indice == pytest.approx(10.0)
    assert fila[0].notas["risco"] is None


def test_sorteio_com_a_mesma_semente_repete_a_amostra() -> None:
    pesos = calcular_pesos(JULGAMENTOS_PADRAO)
    fila = classificar_ocorrencias(
        [ocorrencia("A", idade) for idade in range(20)], [bairro("A", 1.0)], pesos
    )

    assert sortear_amostra(fila, 7) == sortear_amostra(fila, 7)
    assert len(sortear_amostra(fila, 7)) == 3


def test_distribuicao_cobre_as_vinte_faixas_de_nota() -> None:
    fila = classificar_so_pelo_atraso([Ocorrencia(None, 0, dias_alem_do_prazo=1)])

    faixas = distribuir_notas(fila)

    assert len(faixas) == 20
    assert faixas[-1].registros == 1


def test_quintis_repartem_os_bairros() -> None:
    faixas = limites_das_faixas([float(valor) for valor in range(1, 101)])

    assert len(faixas) == 5
    assert classe_da_taxa(1.0, faixas) == 1
    assert classe_da_taxa(100.0, faixas) == 5


def test_quintis_juntam_limites_repetidos() -> None:
    faixas = limites_das_faixas([0.0, 0.0, 0.0, 0.0, 5.0, 9.0])

    assert len(faixas) < 5
    assert faixas[0].inicio == 0.0


def test_taxa_nao_quebra_sem_anos_com_dado() -> None:
    assert calcular_taxa(0, 0, 1000) == 0
    assert calcular_taxa(200, 2, 1000) == 100


def test_sem_taxa_nao_ha_classe() -> None:
    assert classe_da_taxa(None, limites_das_faixas([1.0, 2.0])) is None


def test_tendencia_acompanha_uma_reta() -> None:
    pontos = [Ponto(float(x), 2.0 * x) for x in range(10)]

    tendencia = suavizar(pontos)

    assert len(tendencia) == 10
    assert tendencia[5].y == pytest.approx(10.0)


def test_poucos_pontos_nao_geram_tendencia() -> None:
    assert suavizar([Ponto(1, 1)]) == []


def test_minimo_por_categoria_segue_o_tamanho_do_recorte() -> None:
    assert minimo_de_pedidos_por_categoria(500_000) == 1000
    assert minimo_de_pedidos_por_categoria(100) == 30
