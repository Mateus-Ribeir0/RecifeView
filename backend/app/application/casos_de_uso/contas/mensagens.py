from app.application.portas.contas import MensagemDeEmail
from app.domain.conta import VALIDADE_DO_CODIGO, FinalidadeDoCodigo

MINUTOS_DE_VALIDADE = int(VALIDADE_DO_CODIGO.total_seconds() // 60)
ASSINATURA = "RecifeView\nEste e-mail foi enviado automaticamente. Não responda."

ASSUNTOS = {
    FinalidadeDoCodigo.CONFIRMAR_EMAIL: "Seu código para confirmar a conta no RecifeView",
    FinalidadeDoCodigo.REDEFINIR_SENHA: "Seu código para criar uma nova senha no RecifeView",
}
PEDIDOS = {
    FinalidadeDoCodigo.CONFIRMAR_EMAIL: "Use este código para confirmar o seu e-mail:",
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


def aviso_de_conta_existente(para: str) -> MensagemDeEmail:
    corpo = (
        "Alguém tentou criar uma conta no RecifeView com este e-mail, que já tem conta.\n\n"
        'Se foi você, entre com a sua senha ou use "Esqueci minha senha". '
        "Se não foi, ignore esta mensagem: ninguém entrou na sua conta.\n\n"
        f"{ASSINATURA}"
    )
    return MensagemDeEmail(para, "Tentativa de cadastro com o seu e-mail", corpo)
