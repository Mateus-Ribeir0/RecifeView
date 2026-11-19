from datetime import datetime

from app.application.casos_de_uso.contas.mensagens import ASSINATURA
from app.application.portas.contas import MensagemDeEmail
from app.domain.encaminhamento.orgaos import nome_do_orgao
from app.domain.usuario import Usuario

FORMATO_DA_VALIDADE = "%d/%m/%Y"


def mensagem_de_convite(usuario: Usuario, link: str, expira_em: datetime) -> MensagemDeEmail:
    orgao = nome_do_orgao(usuario.orgao) if usuario.orgao else "seu órgão"
    corpo = (
        f"Olá, {usuario.nome}.\n\n"
        f"A administração da Prefeitura do Recife criou um acesso para você responder, pelo "
        f"RecifeView, às ocorrências encaminhadas a {orgao}.\n\n"
        "Para definir a sua senha e entrar, abra o link abaixo. Ele vale só para você e pode ser "
        f"usado uma vez, até {expira_em.strftime(FORMATO_DA_VALIDADE)}:\n\n"
        f"{link}\n\n"
        "Se você não esperava este convite, ignore a mensagem: nenhum acesso é liberado sem a "
        "senha que você mesmo define.\n\n"
        f"{ASSINATURA}"
    )
    return MensagemDeEmail(str(usuario.email), f"Seu acesso de {orgao} no RecifeView", corpo)
