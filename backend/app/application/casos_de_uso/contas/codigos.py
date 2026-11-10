from dataclasses import dataclass
from uuid import uuid4

from app.application.casos_de_uso.contas.mensagens import mensagem_com_codigo
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import (
    VALIDADE_DO_CODIGO,
    CodigoDeConta,
    FinalidadeDoCodigo,
    calcular_hash_do_codigo,
    gerar_codigo,
)
from app.domain.erros import CodigoInvalido
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class CodigosDeConta:
    servicos: ServicosDeConta

    def emitir(self, usuario: Usuario, finalidade: FinalidadeDoCodigo) -> None:
        """Um código por minuto, no máximo: o reenvio não serve para inundar a caixa de alguém."""
        agora = self.servicos.relogio.agora()
        anterior = self.servicos.codigos.ultimo(usuario.id, finalidade)
        if anterior is not None and anterior.foi_emitido_ha_pouco(agora):
            return
        self.servicos.codigos.invalidar_abertos(usuario.id, finalidade, agora)
        codigo, identificador = gerar_codigo(), uuid4()
        self.servicos.codigos.adicionar(
            CodigoDeConta(
                id=identificador,
                usuario_id=usuario.id,
                finalidade=finalidade,
                hash_do_codigo=calcular_hash_do_codigo(identificador, codigo),
                criado_em=agora,
                expira_em=agora + VALIDADE_DO_CODIGO,
            )
        )
        self.servicos.emails.enviar(mensagem_com_codigo(str(usuario.email), finalidade, codigo))

    def conferir(self, usuario: Usuario, finalidade: FinalidadeDoCodigo, digitado: str) -> None:
        agora = self.servicos.relogio.agora()
        codigo = self.servicos.codigos.ultimo(usuario.id, finalidade)
        if codigo is None or not codigo.pode_ser_usado(agora):
            raise CodigoInvalido
        if not codigo.confere(digitado):
            self.servicos.codigos.atualizar(codigo.com_tentativa())
            evento = EventoDeAcesso(TipoDeEventoDeAcesso.CODIGO_RECUSADO, agora, usuario.id)
            self.servicos.acessos.registrar(evento)
            raise CodigoInvalido
        self.servicos.codigos.atualizar(codigo.usado(agora))
