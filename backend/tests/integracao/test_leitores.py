import gzip
import json
import lzma
import zipfile
from pathlib import Path

import pytest
from openpyxl import Workbook

from app.domain.erros import ArquivoIlegivel
from app.infrastructure.importacao.leitores import LeitorDeArquivos

CSV = "Bairro;Data\nVárzea;2026-01-02\nAfogados;2026-01-03\n"


def ler(caminho: Path) -> tuple[list[str], list[list[str]]]:
    tabela = LeitorDeArquivos().abrir(caminho)
    return tabela.colunas, list(tabela.linhas())


def test_csv_com_ponto_e_virgula_em_utf8(tmp_path: Path) -> None:
    caminho = tmp_path / "a.csv"
    caminho.write_text(CSV, encoding="utf-8")

    colunas, linhas = ler(caminho)

    assert colunas == ["Bairro", "Data"]
    assert linhas[0] == ["Várzea", "2026-01-02"]


def test_csv_em_latin1_e_detectado(tmp_path: Path) -> None:
    caminho = tmp_path / "a.csv"
    caminho.write_bytes(CSV.encode("cp1252"))

    tabela = LeitorDeArquivos().abrir(caminho)

    assert tabela.codificacao == "cp1252"
    assert next(tabela.linhas())[0] == "Várzea"


def test_csv_com_virgula_e_bom(tmp_path: Path) -> None:
    caminho = tmp_path / "a.csv"
    caminho.write_text("﻿Bairro,Data\nAfogados,2026-01-03\n", encoding="utf-8")

    assert ler(caminho)[0] == ["Bairro", "Data"]


def test_linhas_vazias_antes_do_cabecalho_sao_ignoradas(tmp_path: Path) -> None:
    caminho = tmp_path / "a.csv"
    caminho.write_text(";;;\n;;;\n" + CSV, encoding="utf-8")

    colunas, linhas = ler(caminho)

    assert colunas == ["Bairro", "Data"]
    assert len(linhas) == 2


def test_colunas_vazias_no_fim_do_cabecalho_saem(tmp_path: Path) -> None:
    caminho = tmp_path / "a.csv"
    caminho.write_text("Bairro;Data;;;\nAfogados;2026-01-03;;;\n", encoding="utf-8")

    assert ler(caminho)[0] == ["Bairro", "Data"]


def test_nome_de_coluna_repetido_ganha_sufixo(tmp_path: Path) -> None:
    caminho = tmp_path / "a.csv"
    caminho.write_text("Data;Data\n2026-01-03;2026-01-04\n", encoding="utf-8")

    assert ler(caminho)[0] == ["Data", "Data_2"]


def test_zip_abre_o_maior_csv(tmp_path: Path) -> None:
    caminho = tmp_path / "a.zip"
    with zipfile.ZipFile(caminho, "w") as pacote:
        pacote.writestr("leia-me.txt", "x")
        pacote.writestr("dados.csv", CSV)

    assert ler(caminho)[0] == ["Bairro", "Data"]


def test_zip_sem_tabela_e_recusado(tmp_path: Path) -> None:
    caminho = tmp_path / "a.zip"
    with zipfile.ZipFile(caminho, "w") as pacote:
        pacote.writestr("foto.png", "x")

    with pytest.raises(ArquivoIlegivel):
        LeitorDeArquivos().abrir(caminho)


@pytest.mark.parametrize(("nome", "abrir"), [("a.csv.gz", gzip.open), ("a.csv.xz", lzma.open)])
def test_compactados_sao_abertos(tmp_path: Path, nome: str, abrir: object) -> None:
    caminho = tmp_path / nome
    with abrir(caminho, "wt", encoding="utf-8") as saida:  # type: ignore[operator]
        saida.write(CSV)

    assert ler(caminho)[0] == ["Bairro", "Data"]


def test_json_com_lista_de_registros(tmp_path: Path) -> None:
    caminho = tmp_path / "a.json"
    caminho.write_text(json.dumps([{"Bairro": "Afogados", "Total": 3}]), encoding="utf-8")

    colunas, linhas = ler(caminho)

    assert colunas == ["Bairro", "Total"]
    assert linhas == [["Afogados", "3"]]


def test_json_no_formato_do_portal(tmp_path: Path) -> None:
    caminho = tmp_path / "a.json"
    conteudo = {"result": {"records": [{"Bairro": "Afogados"}]}}
    caminho.write_text(json.dumps(conteudo), encoding="utf-8")

    assert ler(caminho)[1] == [["Afogados"]]


def test_json_invalido_e_recusado(tmp_path: Path) -> None:
    caminho = tmp_path / "a.json"
    caminho.write_text("{nao e json", encoding="utf-8")

    with pytest.raises(ArquivoIlegivel):
        LeitorDeArquivos().abrir(caminho)


def test_planilha_xlsx(tmp_path: Path) -> None:
    caminho = tmp_path / "a.xlsx"
    planilha = Workbook()
    aba = planilha.active
    assert aba is not None
    aba.append(["Bairro", "Total"])
    aba.append(["Afogados", 3.0])
    planilha.save(caminho)

    colunas, linhas = ler(caminho)

    assert colunas == ["Bairro", "Total"]
    assert linhas == [["Afogados", "3"]]
