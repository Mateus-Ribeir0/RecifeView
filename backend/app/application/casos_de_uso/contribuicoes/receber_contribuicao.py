from dataclasses import dataclass, replace
from datetime import timedelta
from uuid import uuid4

from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.portas.contribuicoes import ParNovo
from app.domain.contribuicao.catalogo import ServicoDoFormulario, localizar_servico
from app.domain.contribuicao.comparacao import (
    DIAS_DE_REINCIDENCIA,
    ClasseDaComparacao,
    comparar_relatos,
)
from app.domain.contribuicao.contribuicao import (
    Contribuicao,
    FormularioPreenchido,
    ResultadoDoEnvio,
    exigir_tamanhos,
    exigir_texto_sem_dado_pessoal,
)
from app.domain.contribuicao.enderecos import reconhecer_logradouro
from app.domain.erros import ContribuicaoInvalida
from app.domain.importacao.pseudonimizacao import gerar_id_local, numero_foi_informado


@dataclass(frozen=True)
class Avaliacao:
    principal: Contribuicao | None
    pares: list[ParNovo]


def _avaliar(nova: Contribuicao, candidatas: list[Contribuicao]) -> Avaliacao:
    relato = nova.como_relato()
    comparadas = [
        (candidata, comparar_relatos(candidata.como_relato(), relato)) for candidata in candidatas
    ]
    iguais = [c for c, comparacao in comparadas if comparacao.classe is ClasseDaComparacao.MESMA]
    if iguais:
        return Avaliacao(min(iguais, key=lambda candidata: candidata.recebida_em), [])
    pares = [
        ParNovo(candidata.id, comparacao)
        for candidata, comparacao in comparadas
        if comparacao.classe is ClasseDaComparacao.PROVAVEL
    ]
    return Avaliacao(None, pares)


@dataclass(frozen=True)
class ReceberContribuicao:
    """Guarda o relato em quarentena: nada do que chega aqui aparece no painel sem revisão."""

    servicos: ServicosDeContribuicoes

    def executar(self, formulario: FormularioPreenchido) -> ResultadoDoEnvio:
        repetido = self.servicos.contribuicoes.buscar_por_chave_de_envio(formulario.chave_de_envio)
        if repetido is not None:
            return repetido.resultado
        servico = localizar_servico(formulario.servico_codigo)
        self._validar(formulario)
        nova = self._montar(formulario, servico)
        desde = nova.data_relato - timedelta(days=DIAS_DE_REINCIDENCIA - 1)
        candidatas = self.servicos.contribuicoes.candidatas(
            nova.bairro_oficial, nova.categoria, desde
        )
        avaliacao = _avaliar(nova, candidatas)
        guardada = self.servicos.contribuicoes.inserir(
            self._com_resultado(nova, avaliacao), avaliacao.pares
        )
        return guardada.resultado

    def _validar(self, formulario: FormularioPreenchido) -> None:
        exigir_tamanhos(formulario)
        exigir_texto_sem_dado_pessoal("logradouro", formulario.logradouro)
        exigir_texto_sem_dado_pessoal("detalhe", formulario.detalhe)
        bairros = {bairro.chave for bairro in self.servicos.referencia.bairros()}
        if formulario.bairro_oficial not in bairros:
            raise ContribuicaoInvalida("bairro", "Escolha um dos bairros do Recife.")

    def _montar(
        self, formulario: FormularioPreenchido, servico: ServicoDoFormulario
    ) -> Contribuicao:
        agora = self.servicos.relogio.agora()
        conhecidas = self.servicos.referencia.logradouros(formulario.bairro_oficial)
        logradouro = reconhecer_logradouro(formulario.logradouro, conhecidas)
        numero = formulario.numero.strip().upper()
        sal = self.servicos.sal
        return Contribuicao(
            id=uuid4(),
            chave_de_envio=formulario.chave_de_envio,
            recebida_em=agora,
            data_relato=agora.date(),
            categoria=servico.categoria,
            servico_codigo=servico.codigo,
            servico=servico.nome_na_fonte,
            bairro_oficial=formulario.bairro_oficial,
            logradouro=logradouro,
            numero=numero or None,
            detalhe=formulario.detalhe.strip() or None,
            id_local=gerar_id_local((logradouro, numero), sal) if sal else None,
            numero_informado=numero_foi_informado(numero),
            retorno=formulario.retorno,
            resultado=ResultadoDoEnvio.NOVA,
        )

    @staticmethod
    def _com_resultado(nova: Contribuicao, avaliacao: Avaliacao) -> Contribuicao:
        if avaliacao.principal is not None:
            return replace(
                nova, principal_id=avaliacao.principal.id, resultado=ResultadoDoEnvio.SOMADA
            )
        if avaliacao.pares:
            return replace(nova, resultado=ResultadoDoEnvio.EM_CONFERENCIA)
        return nova
