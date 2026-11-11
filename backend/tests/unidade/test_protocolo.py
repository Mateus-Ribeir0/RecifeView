import pytest

from app.domain.erros import ProtocoloInvalido
from app.domain.protocolo import exigir_protocolo, normalizar_protocolo


def test_protocolo_perde_espacos_e_vira_maiusculas() -> None:
    assert normalizar_protocolo(" 2025 / ab-12 ") == "2025/AB-12"


def test_protocolo_vazio_vira_nada() -> None:
    assert normalizar_protocolo("   ") is None


@pytest.mark.parametrize("digitado", ["", "12", "2025#123", "x" * 41, "rua do sol, 10"])
def test_consulta_recusa_protocolo_fora_do_formato(digitado: str) -> None:
    with pytest.raises(ProtocoloInvalido):
        exigir_protocolo(digitado)


def test_consulta_aceita_protocolo_com_barra_ponto_e_hifen() -> None:
    assert exigir_protocolo("2025.000123/OUV-1") == "2025.000123/OUV-1"
