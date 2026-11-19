from datetime import timedelta
from uuid import UUID

import pytest

from app.application.casos_de_uso.acessos_corporativos.acessos import (
    CriarAcessoCorporativo,
    DadosDoAcesso,
    DesativarAcesso,
    EditarAcessoCorporativo,
    ExcluirAcesso,
    ListarAcessosCorporativos,
    NovoAcesso,
    ReativarAcesso,
    ReenviarConvite,
)
from app.application.casos_de_uso.acessos_corporativos.convite import AbrirConvite, AceitarConvite
from app.domain.acesso import TipoDeEventoDeAcesso
from app.domain.acesso_corporativo import VALIDADE_DO_CONVITE, SituacaoDoAcesso
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import (
    AcaoSoDaAdministracao,
    AcessoCorporativoNaoEncontrado,
    ConviteInvalido,
    ConviteJaAceito,
    EmailJaCadastrado,
    SenhaFraca,
)
from app.domain.usuario import Perfil
from tests.fakes import criar_usuario
from tests.fakes_corporativo import AmbienteDeAcessos

EMAIL_DA_COMPESA = "responsavel@compesa.exemplo"
NOVO_ACESSO = NovoAcesso(EMAIL_DA_COMPESA, DadosDoAcesso("Ana Souza", Orgao.COMPESA))
SENHA_FORTE = "Compesa@Recife2026"


def criar(ambiente: AmbienteDeAcessos) -> None:
    CriarAcessoCorporativo(ambiente.servicos()).executar(NOVO_ACESSO, ambiente.administradora)


def id_do_acesso(ambiente: AmbienteDeAcessos) -> UUID:
    (acesso,) = ListarAcessosCorporativos(ambiente.servicos()).executar()
    return acesso.usuario_id


def test_administracao_cria_o_acesso_e_manda_o_convite() -> None:
    ambiente = AmbienteDeAcessos()

    criar(ambiente)

    (acesso,) = ListarAcessosCorporativos(ambiente.servicos()).executar()
    (mensagem,) = ambiente.emails.mensagens
    assert acesso.orgao is Orgao.COMPESA
    assert acesso.situacao(ambiente.relogio.agora()) is SituacaoDoAcesso.CONVITE_ENVIADO
    assert mensagem.para == EMAIL_DA_COMPESA
    assert "https://recifeview.exemplo/convite/" in mensagem.corpo
    assert "Compesa" in mensagem.assunto
    assert ambiente.eventos() == [
        TipoDeEventoDeAcesso.CONTA_CRIADA,
        TipoDeEventoDeAcesso.CONVITE_ENVIADO,
    ]


def test_conta_criada_nao_entra_antes_do_convite() -> None:
    ambiente = AmbienteDeAcessos()

    criar(ambiente)

    conta = ambiente.usuarios.buscar_por_id(id_do_acesso(ambiente))
    assert conta is not None
    assert conta.perfil is Perfil.CORPORATIVO
    assert not ambiente.senhas.confere(SENHA_FORTE, conta.hash_da_senha)


def test_gestao_publica_ve_mas_nao_cria_acesso() -> None:
    ambiente = AmbienteDeAcessos()
    gestora = criar_usuario(perfil=Perfil.GESTOR)

    with pytest.raises(AcaoSoDaAdministracao):
        CriarAcessoCorporativo(ambiente.servicos()).executar(NOVO_ACESSO, gestora)
    assert ambiente.emails.mensagens == []


def test_email_ja_usado_por_outra_conta_e_recusado() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)

    with pytest.raises(EmailJaCadastrado):
        criar(ambiente)


def test_convite_aceito_define_a_senha_e_ja_abre_a_sessao() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)
    token = ambiente.token_do_ultimo_convite()

    aberto = AbrirConvite(ambiente.servicos()).executar(token)
    sessao = AceitarConvite(ambiente.servicos()).executar(token, SENHA_FORTE)

    assert (aberto.nome, aberto.orgao) == ("Ana Souza", Orgao.COMPESA)
    assert sessao.acesso.usuario.e_corporativo
    assert ambiente.senhas.confere(SENHA_FORTE, sessao.acesso.usuario.hash_da_senha)
    (acesso,) = ListarAcessosCorporativos(ambiente.servicos()).executar()
    assert acesso.situacao(ambiente.relogio.agora()) is SituacaoDoAcesso.ATIVO


def test_convite_nao_vale_duas_vezes() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)
    token = ambiente.token_do_ultimo_convite()
    AceitarConvite(ambiente.servicos()).executar(token, SENHA_FORTE)

    with pytest.raises(ConviteInvalido):
        AceitarConvite(ambiente.servicos()).executar(token, SENHA_FORTE)


def test_convite_vencido_e_recusado() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)
    token = ambiente.token_do_ultimo_convite()
    ambiente.relogio.avancar(VALIDADE_DO_CONVITE + timedelta(minutes=1))

    with pytest.raises(ConviteInvalido):
        AbrirConvite(ambiente.servicos()).executar(token)


def test_senha_fraca_nao_aceita_o_convite() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)

    with pytest.raises(SenhaFraca):
        AceitarConvite(ambiente.servicos()).executar(ambiente.token_do_ultimo_convite(), "123")


def test_convite_novo_substitui_o_anterior() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)
    antigo = ambiente.token_do_ultimo_convite()
    usuario_id = id_do_acesso(ambiente)

    ReenviarConvite(ambiente.servicos()).executar(usuario_id, ambiente.administradora)

    with pytest.raises(ConviteInvalido):
        AbrirConvite(ambiente.servicos()).executar(antigo)
    AbrirConvite(ambiente.servicos()).executar(ambiente.token_do_ultimo_convite())


def test_convite_ja_aceito_nao_e_reenviado() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)
    AceitarConvite(ambiente.servicos()).executar(ambiente.token_do_ultimo_convite(), SENHA_FORTE)

    with pytest.raises(ConviteJaAceito):
        ReenviarConvite(ambiente.servicos()).executar(
            id_do_acesso(ambiente),
            ambiente.administradora,
        )


def test_desativar_derruba_as_sessoes_e_o_convite_aberto() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)
    token = ambiente.token_do_ultimo_convite()
    usuario_id = id_do_acesso(ambiente)

    desativado = DesativarAcesso(ambiente.servicos()).executar(
        usuario_id,
        ambiente.administradora,
    )

    assert desativado.situacao(ambiente.relogio.agora()) is SituacaoDoAcesso.DESATIVADO
    assert ambiente.sessoes_guardadas.ativas() == []
    with pytest.raises(ConviteInvalido):
        AbrirConvite(ambiente.servicos()).executar(token)
    reativado = ReativarAcesso(ambiente.servicos()).executar(
        usuario_id,
        ambiente.administradora,
    )
    assert reativado.situacao(ambiente.relogio.agora()) is SituacaoDoAcesso.CONVITE_VENCIDO


def test_editar_corrige_o_nome_e_o_orgao() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)

    editado = EditarAcessoCorporativo(ambiente.servicos()).executar(
        id_do_acesso(ambiente),
        DadosDoAcesso("Ana  Maria Souza", Orgao.NEOENERGIA),
        ambiente.administradora,
    )

    assert (editado.nome, editado.orgao) == ("Ana Maria Souza", Orgao.NEOENERGIA)


def test_excluir_tira_nome_e_email_e_a_conta_some_da_lista() -> None:
    ambiente = AmbienteDeAcessos()
    criar(ambiente)
    usuario_id = id_do_acesso(ambiente)

    ExcluirAcesso(ambiente.servicos()).executar(usuario_id, ambiente.administradora)

    conta = ambiente.usuarios.buscar_por_id(usuario_id)
    assert conta is not None
    assert conta.foi_excluido
    assert not conta.ativo
    assert EMAIL_DA_COMPESA not in str(conta.email)
    assert ListarAcessosCorporativos(ambiente.servicos()).executar() == []
    with pytest.raises(AcessoCorporativoNaoEncontrado):
        ReativarAcesso(ambiente.servicos()).executar(usuario_id, ambiente.administradora)
