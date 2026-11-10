from app.application.portas.contas import MensagemDeEmail
from app.domain.conta import VALIDADE_DO_CODIGO, FinalidadeDoCodigo

MINUTOS_DE_VALIDADE = int(VALIDADE_DO_CODIGO.total_seconds() // 60)
ASSINATURA = "RecifeView\nEste e-mail foi enviado automaticamente. Não responda."

ASSUNTOS = {
    FinalidadeDoCodigo.REDEFINIR_SENHA: "Seu código para criar uma nova senha no RecifeView",
}
PEDIDOS = {
    FinalidadeDoCodigo.REDEFINIR_SENHA: "Use este código para criar uma nova senha:",
}


def mensagem_com_codigo(para: str, finalidade: FinalidadeDoCodigo, codigo: str) -> MensagemDeEmail:
    corpo = (
        f"{PEDIDOS[finalidade]}\n\n{codigo[:3]} {codigo[3:]}\n\n"
        f"O código vale por {MINUTOS_DE_VALIDADE} minutos. "
        "Se você não pediu, ignore esta mensagem: nada muda na sua conta.\n\n"
        f"{ASSINATURA}"
    )
    return MensagemDeEmail(para, ASSUNTOS[finalidade], corpo)
