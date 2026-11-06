from app.application.portas.importacoes import ContribuicoesDaImportacao, RegistroNoMesmoLocal
from app.domain.contribuicao.comparacao import (
    ClasseDaComparacao,
    Comparacao,
    Relato,
    comparar_relatos,
)
from app.domain.contribuicao.conferencia import (
    Coincidencia,
    ResultadoDaConferencia,
    chave_da_contribuicao,
    descrever_coincidencia,
    relato_da_linha,
)
from app.domain.fontes import ROTULOS_DAS_FONTES, Fonte
from app.domain.importacao.registro import EnderecoDaLinha, RegistroDeDemanda


def _relato_da_base(registro: RegistroNoMesmoLocal) -> Relato:
    return Relato(
        data=registro.data_abertura,
        bairro=registro.bairro_oficial,
        categoria=registro.categoria,
        servico_codigo=registro.servico_codigo,
        id_local=registro.id_local,
        numero_informado=registro.numero_informado,
    )


class ConferenciaDoPacote:
    """Procura na base os pedidos das outras fontes no mesmo local dos relatos do pacote.

    A base guarda só o pseudônimo do endereço, então a comparação depende do sal: sem ele, os
    relatos do pacote ficam em `sem_endereco` e a tela avisa.
    """

    def __init__(self, contribuicoes: ContribuicoesDaImportacao, importacao_id: int) -> None:
        self._contribuicoes = contribuicoes
        self._importacao_id = importacao_id
        self._registros: list[RegistroDeDemanda] = []
        self._resultado = ResultadoDaConferencia()

    def conferir(self, registro: RegistroDeDemanda, endereco: EnderecoDaLinha | None) -> None:
        self._resultado.comparadas += 1
        if registro.id_local is None:
            self._resultado.sem_endereco += 1
            return
        self._registros.append(registro)

    def concluir(self) -> ResultadoDaConferencia:
        if not self._registros:
            return self._resultado
        ids_por_chave = {
            chave_da_contribuicao(contribuicao_id): contribuicao_id
            for contribuicao_id in self._contribuicoes.ids_do_pacote(self._importacao_id)
        }
        locais = [str(registro.id_local) for registro in self._registros]
        na_base = self._contribuicoes.registros_no_mesmo_local(locais)
        for registro in self._registros:
            coincidencia = self._melhor_da_base(registro, na_base)
            contribuicao_id = ids_por_chave.get(registro.chave_registro)
            if coincidencia is not None and contribuicao_id is not None:
                self._resultado.coincidencias.append(
                    Coincidencia(
                        contribuicao_id,
                        coincidencia[0],
                        coincidencia[1],
                        registro.chave_registro,
                    )
                )
        return self._resultado

    @staticmethod
    def _melhor_da_base(
        registro: RegistroDeDemanda, na_base: list[RegistroNoMesmoLocal]
    ) -> tuple[Comparacao, str] | None:
        relato = relato_da_linha(registro, None)
        if relato is None:
            return None
        melhor = None
        for candidato in na_base:
            if candidato.id_local != registro.id_local:
                continue
            comparacao = comparar_relatos(relato, _relato_da_base(candidato))
            if comparacao.classe is ClasseDaComparacao.DISTINTA:
                continue
            if melhor is None or comparacao.pontuacao > melhor[0].pontuacao:
                rotulo = ROTULOS_DAS_FONTES[Fonte(candidato.fonte)]
                melhor = (comparacao, descrever_coincidencia(rotulo, comparacao))
        return melhor
