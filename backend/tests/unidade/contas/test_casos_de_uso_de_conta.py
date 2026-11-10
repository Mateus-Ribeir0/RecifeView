from datetime import timedelta

import pytest

from app.application.casos_de_uso.contas import codigos
from app.application.casos_de_uso.contas.confirmar_email import (
    ConfirmacaoDeEmail,
    ConfirmarEmail,
)
from app.application.casos_de_uso.contas.criar_conta import CriarConta, NovaConta
from app.application.casos_de_uso.contas.minha_conta import (
    AtualizarMinhaConta,
    ExcluirMinhaConta,
)
from app.application.casos_de_uso.contas.recuperar_senha import (
    CriarNovaSenha,
    NovaSenhaComCodigo,
    PedirNovaSenha,
)
from app.application.casos_de_uso.contas.reenviar_codigo import ReenviarCodigoDeConfirmacao
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.application.casos_de_uso.entrar import Entrar
from app.application.sessoes import GestaoDeSessoes
from app.domain.acesso import AreaDeAcesso, TipoDeEventoDeAcesso
from app.domain.conta import FinalidadeDoCodigo
from app.domain.email import Email
from app.domain.erros import (
    AcessoNegado,
    AreaDaGestaoNegada,
    CadastroInvalido,
    CodigoInvalido,
    EmailNaoConfirmado,
    SenhaAtualIncorreta,
    SenhaFraca,
)
from app.domain.usuario import Perfil, Usuario
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import (
    SENHA_DE_TESTE,
    AcessosEmMemoria,
    CaixaDeEmailsEmMemoria,
    CodigosEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
    criar_usuario,
)

EMAIL = "morador@exemplo.com"
SENHA = "uma senha bem comprida"
BAIRROS = frozenset({"AFOGADOS", "IPUTINGA"})


class Ambiente:
    def __init__(self, *usuarios: object) -> None:
        self.relogio = RelogioFixo()
        self.usuarios = UsuariosEmMemoria(*usuarios)  # type: ignore[arg-type]
        self.sessoes_guardadas = SessoesEmMemoria()
        self.emails = CaixaDeEmailsEmMemoria()
        self.acessos = AcessosEmMemoria()
        self.codigos = CodigosEmMemoria()
        emissor = EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15))
        self.servicos = ServicosDeConta(
            usuarios=self.usuarios,
            codigos=self.codigos,
            senhas=HashDeSenhaDeTeste(),
            emails=self.emails,
            acessos=self.acessos,
            sessoes=GestaoDeSessoes(self.sessoes_guardadas, emissor, self.relogio),
            relogio=self.relogio,
        )

    def cadastrar(self, senha: str = SENHA, **mudancas: object) -> None:
        dados = {
            "nome": "Maria da Silva",
            "email": EMAIL,
            "senha": senha,
            "bairro_oficial": "AFOGADOS",
            "aceitou_os_termos": True,
            **mudancas,
        }
        CriarConta(self.servicos, BAIRROS).executar(NovaConta(**dados))  # type: ignore[arg-type]

    def confirmar(self, codigo: str | None = None, senha: str = SENHA) -> None:
        digitado = codigo or self.emails.ultimo_codigo()
        ConfirmarEmail(self.servicos).executar(ConfirmacaoDeEmail(EMAIL, digitado, senha))

    def conta_ou_nada(self) -> Usuario | None:
        return self.usuarios.buscar_por_email(Email(EMAIL))

    def conta(self) -> Usuario:
        conta = self.conta_ou_nada()
        assert conta is not None
        return conta


def test_cadastro_cria_conta_pendente_e_envia_codigo() -> None:
    ambiente = Ambiente()

    ambiente.cadastrar()

    conta = ambiente.conta()
    assert conta.perfil is Perfil.CIDADAO
    assert conta.precisa_confirmar_email
    assert conta.bairro_oficial == "AFOGADOS"
    assert len(ambiente.emails.mensagens) == 1
    assert SENHA not in ambiente.emails.mensagens[0].corpo
    assert TipoDeEventoDeAcesso.CONTA_CRIADA in ambiente.acessos.tipos()


def test_email_que_ja_tem_conta_recebe_aviso_e_nada_muda() -> None:
    gestora = criar_usuario(email=Email(EMAIL))
    ambiente = Ambiente(gestora)

    ambiente.cadastrar()

    assert ambiente.conta() == gestora
    assert ambiente.emails.mensagens[-1].assunto == "Tentativa de cadastro com o seu e-mail"


def test_confirmar_com_codigo_e_senha_abre_a_sessao() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()

    ambiente.confirmar()

    assert not ambiente.conta().precisa_confirmar_email
    assert len(ambiente.sessoes_guardadas.ativas()) == 1


def test_quem_cadastrou_email_alheio_nao_entra_quando_o_dono_confirma() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar(senha="senha do invasor 123")
    ambiente.relogio.avancar(timedelta(minutes=2))
    ambiente.cadastrar(senha=SENHA)

    with pytest.raises(CodigoInvalido):
        ambiente.confirmar(senha="senha do invasor 123")
    ambiente.confirmar(senha=SENHA)
    assert not ambiente.conta().precisa_confirmar_email


@pytest.fixture
def codigos_previsiveis(monkeypatch: pytest.MonkeyPatch) -> None:
    sequencia = iter(["111111", "222222", "333333"])
    monkeypatch.setattr(codigos, "gerar_codigo", lambda: next(sequencia))


@pytest.mark.usefixtures("codigos_previsiveis")
def test_codigo_errado_conta_tentativa() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()

    with pytest.raises(CodigoInvalido):
        ambiente.confirmar(codigo="999999")

    assert TipoDeEventoDeAcesso.CODIGO_RECUSADO in ambiente.acessos.tipos()
    conta = ambiente.conta()
    ultimo = ambiente.codigos.ultimo(conta.id, FinalidadeDoCodigo.CONFIRMAR_EMAIL)
    assert ultimo is not None
    assert ultimo.tentativas == 1


@pytest.mark.usefixtures("codigos_previsiveis")
def test_codigo_antigo_nao_vale_depois_do_reenvio() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()
    ambiente.relogio.avancar(timedelta(minutes=2))
    ReenviarCodigoDeConfirmacao(ambiente.servicos).executar(EMAIL)

    with pytest.raises(CodigoInvalido):
        ambiente.confirmar(codigo="111111")
    ambiente.confirmar(codigo="222222")


def test_codigo_vencido_e_recusado() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()
    ambiente.relogio.avancar(timedelta(minutes=16))

    with pytest.raises(CodigoInvalido):
        ambiente.confirmar()


def test_reenvio_em_menos_de_um_minuto_nao_manda_outro_email() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()

    ReenviarCodigoDeConfirmacao(ambiente.servicos).executar(EMAIL)

    assert len(ambiente.emails.mensagens) == 1


@pytest.mark.parametrize(
    ("mudanca", "campo"),
    [
        ({"aceitou_os_termos": False}, "termos"),
        ({"nome": "R2D2"}, "nome"),
        ({"bairro_oficial": "COPACABANA"}, "bairro"),
    ],
)
def test_cadastro_recusa_campo_invalido(mudanca: dict[str, object], campo: str) -> None:
    with pytest.raises(CadastroInvalido) as erro:
        Ambiente().cadastrar(**mudanca)  # type: ignore[arg-type]
    assert erro.value.campo == campo


def test_cadastro_recusa_senha_fraca() -> None:
    with pytest.raises(SenhaFraca):
        Ambiente().cadastrar(senha="curta")


def entrar(ambiente: Ambiente, area: AreaDeAcesso) -> None:
    caso = Entrar(
        ambiente.usuarios,
        HashDeSenhaDeTeste(),
        ambiente.servicos.sessoes,
        ambiente.acessos,
        ambiente.relogio,
    )
    caso.executar(EMAIL, SENHA, area)


def test_cidadao_sem_confirmacao_nao_entra() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()

    with pytest.raises(EmailNaoConfirmado):
        entrar(ambiente, AreaDeAcesso.CIDADE)


def test_cidadao_nao_entra_pela_area_da_gestao() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()
    ambiente.confirmar()

    with pytest.raises(AreaDaGestaoNegada):
        entrar(ambiente, AreaDeAcesso.GESTAO)
    entrar(ambiente, AreaDeAcesso.CIDADE)


def test_recuperar_senha_troca_a_senha_e_derruba_as_sessoes() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()
    ambiente.confirmar()

    PedirNovaSenha(ambiente.servicos).executar(EMAIL)
    codigo = ambiente.emails.ultimo_codigo()
    nova = NovaSenhaComCodigo(EMAIL, codigo, "outra senha bem comprida")
    CriarNovaSenha(ambiente.servicos).executar(nova)

    assert ambiente.sessoes_guardadas.ativas() == []
    assert ambiente.conta().hash_da_senha == HashDeSenhaDeTeste().gerar(nova.nova_senha)


def test_conta_da_gestao_nao_recupera_senha_por_e_mail() -> None:
    ambiente = Ambiente(criar_usuario(email=Email(EMAIL)))

    PedirNovaSenha(ambiente.servicos).executar(EMAIL)

    assert ambiente.emails.mensagens == []


def test_excluir_conta_pede_a_senha_e_apaga_os_dados() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()
    ambiente.confirmar()
    conta = ambiente.conta()

    with pytest.raises(SenhaAtualIncorreta):
        ExcluirMinhaConta(ambiente.servicos).executar(conta, "errada")
    ExcluirMinhaConta(ambiente.servicos).executar(conta, SENHA)

    assert ambiente.conta_ou_nada() is None
    excluida = ambiente.usuarios.buscar_por_id(conta.id)
    assert excluida is not None
    assert not excluida.ativo
    assert ambiente.sessoes_guardadas.ativas() == []


def test_conta_da_gestao_nao_se_exclui_sozinha() -> None:
    gestora = criar_usuario()
    with pytest.raises(AcessoNegado):
        ExcluirMinhaConta(Ambiente(gestora).servicos).executar(gestora, SENHA_DE_TESTE)


def test_atualizar_bairro_e_nome() -> None:
    ambiente = Ambiente()
    ambiente.cadastrar()
    conta = ambiente.conta()

    atualizada = AtualizarMinhaConta(ambiente.servicos, BAIRROS).executar(
        conta, " Maria  Souza ", "IPUTINGA"
    )

    assert (atualizada.nome, atualizada.bairro_oficial) == ("Maria Souza", "IPUTINGA")
