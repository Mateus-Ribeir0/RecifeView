from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date

from app.domain.fontes import Fonte
from app.domain.importacao.campos import (
    CAMPOS_DE_DATA,
    CAMPOS_POR_NOME,
    CAMPOS_VERIFICADOS_NO_VOCABULARIO,
    TipoDeCampo,
)
from app.domain.importacao.chaves import GeradorDeChaves, OrdemPorConteudo
from app.domain.importacao.conversao import (
    ano_do_nome_do_arquivo,
    calcular_hash,
    ler_booleano,
    ler_inteiro,
)
from app.domain.importacao.correcoes import (
    CATEGORIAS_DO_156,
    ORGAOS_DA_OUVIDORIA,
    SITUACOES_EQUIVALENTES_DO_156,
    situacao_da_ouvidoria_esta_quebrada,
)
from app.domain.importacao.datas import FormatoDeData, interpretar_data
from app.domain.importacao.decisoes import (
    ACEITAR_COMO_NOVO,
    DEIXAR_VAZIO,
    DESCARTAR_LINHA,
    Decisoes,
    PoliticaDeDatasInvalidas,
    PoliticaDeDuplicados,
    PoliticaDeRepetidos,
)
from app.domain.importacao.defesa_civil import adaptar_linha_da_defesa_civil
from app.domain.importacao.layouts import (
    AUXILIAR_LOCALIDADE,
    ENDERECO,
    NUMERO,
    TEXTO_LIVRE,
    CodigoDoLayout,
)
from app.domain.importacao.linha_recusada import LinhaRecusada, recusar
from app.domain.importacao.privacidade import motivo_pelo_conteudo
from app.domain.importacao.pseudonimizacao import gerar_id_local, numero_foi_informado
from app.domain.importacao.registro import EnderecoDaLinha, RegistroDeDemanda
from app.domain.importacao.relatorio import Correcao, MotivoDeDescarte, RelatorioDeLinhas
from app.domain.importacao.territorio_da_linha import (
    ResolvedorDeTerritorio,
    TerritorioResolvido,
    decidir_valor,
)
from app.domain.importacao.texto import normalizar_texto

CAMPOS_COM_TEXTO_LIVRE_DA_FONTE = (
    "categoria",
    "servico",
    "tipo_registro",
    "orgao",
    "canal_entrada",
    "situacao",
)


INDICE_DA_FONTE = 0
INDICE_DA_ABERTURA = 2
INDICE_DO_MOVIMENTO = 3
INDICE_DO_BAIRRO = 12
LAYOUTS_JA_NORMALIZADOS = frozenset({CodigoDoLayout.DATASET, CodigoDoLayout.FORMULARIO})


@dataclass(frozen=True)
class PlanoDeNormalizacao:
    colunas: tuple[str, ...]
    layout: CodigoDoLayout
    decisoes: Decisoes
    arquivo_origem: str
    data_do_retrato: date
    importacao_id: int
    sal: str | None = None


@dataclass(frozen=True)
class Referencias:
    bairros: dict[str, str]
    vocabularios: dict[tuple[str, str], frozenset[str]]


@dataclass(frozen=True)
class PrazoResolvido:
    dias: int | None
    negativo: bool


class NormalizadorDeLinhas:
    """Transforma cada linha do arquivo num registro da base, seguindo as decisões da importação."""

    def __init__(
        self,
        plano: PlanoDeNormalizacao,
        referencias: Referencias,
        ordem: OrdemPorConteudo,
    ) -> None:
        self.relatorio = RelatorioDeLinhas()
        self._plano = plano
        self._decisoes = plano.decisoes
        self._referencias = referencias
        self._leitura = [
            (plano.decisoes.mapeamento[coluna], indice)
            for indice, coluna in enumerate(plano.colunas)
            if plano.decisoes.mapeamento.get(coluna)
        ]
        self._campos_mapeados = {campo for campo, _ in self._leitura}
        self._ultima_coluna_usada = max((indice for _, indice in self._leitura), default=0)
        self._indices_dos_campos = dict(self._leitura)
        self._ja_normalizado = plano.layout in LAYOUTS_JA_NORMALIZADOS
        self._formato_barra = plano.decisoes.formato_de_data or FormatoDeData.DIA_MES_ANO
        self._territorio = ResolvedorDeTerritorio(
            referencias.bairros, plano.decisoes, self._campos_mapeados, self.relatorio
        )
        self._anotando = False
        self._chaves = GeradorDeChaves(
            ordem,
            str(plano.importacao_id)
            if plano.decisoes.repetidos_na_base is PoliticaDeRepetidos.INSERIR_COMO_NOVOS
            else "",
        )
        self._ano_do_arquivo = (
            ano_do_nome_do_arquivo(plano.arquivo_origem) or plano.data_do_retrato.year
        )
        self._adaptar = self._escolher_adaptador()

    def anotar(self, celulas: Sequence[str]) -> None:
        """Primeira passada pelo arquivo: registra o conteúdo para a ordem dos repetidos."""
        self._anotando = True
        self.normalizar(celulas)
        self._anotando = False

    def normalizar(self, celulas: Sequence[str]) -> RegistroDeDemanda | None:
        self.relatorio.lidas += 1
        try:
            registro = self._montar_registro(celulas)
        except LinhaRecusada as recusa:
            self.relatorio.descartes[recusa.motivo] += 1
            return None
        self.relatorio.aceitas += 1
        self.relatorio.fontes[registro.fonte] += 1
        return registro

    def endereco_da_linha(self, celulas: Sequence[str]) -> EnderecoDaLinha | None:
        """Lê o endereço só para o pente fino, que compara e descarta sem guardar."""
        coluna_da_via = self._indices_dos_campos.get(ENDERECO)
        if coluna_da_via is None or coluna_da_via >= len(celulas) or not celulas[coluna_da_via]:
            return None
        coluna_do_numero = self._indices_dos_campos.get(NUMERO, len(celulas))
        numero = celulas[coluna_do_numero] if coluna_do_numero < len(celulas) else ""
        return EnderecoDaLinha(celulas[coluna_da_via], numero)

    def _escolher_adaptador(self) -> Callable[[dict[str, str]], None]:
        adaptadores: dict[CodigoDoLayout, Callable[[dict[str, str]], None]] = {
            CodigoDoLayout.PORTAL_DEFESA_CIVIL: adaptar_linha_da_defesa_civil,
            CodigoDoLayout.PORTAL_OUVIDORIA: self._adaptar_linha_da_ouvidoria,
            CodigoDoLayout.PORTAL_156: self._adaptar_linha_do_156,
        }
        return adaptadores.get(self._plano.layout, lambda _: None)

    @staticmethod
    def _adaptar_linha_da_ouvidoria(valores: dict[str, str]) -> None:
        if situacao_da_ouvidoria_esta_quebrada(valores.get("situacao", "")):
            recusar(MotivoDeDescarte.LINHA_QUEBRADA)
        valores["servico"] = valores.get("categoria", "")

    @staticmethod
    def _adaptar_linha_do_156(valores: dict[str, str]) -> None:
        situacao = valores.get("situacao", "")
        valores["situacao"] = SITUACOES_EQUIVALENTES_DO_156.get(situacao, situacao)

    def _ler_valores(self, celulas: Sequence[str]) -> dict[str, str]:
        if len(celulas) <= self._ultima_coluna_usada:
            recusar(MotivoDeDescarte.LINHA_QUEBRADA)
        valores = {campo: celulas[indice] for campo, indice in self._leitura}
        valores.update(self._decisoes.valores_fixos)
        if self._ja_normalizado:
            return valores
        for campo, valor in valores.items():
            if self._campo_e_texto(campo) and valor:
                valores[campo] = normalizar_texto(valor)
        return valores

    @staticmethod
    def _campo_e_texto(campo: str) -> bool:
        definicao = CAMPOS_POR_NOME.get(campo)
        if definicao is None:
            return campo not in (ENDERECO, NUMERO, TEXTO_LIVRE)
        return definicao.tipo is TipoDeCampo.TEXTO

    def _identificar_fonte(self, valores: dict[str, str]) -> str:
        fonte = valores.get("fonte") or (
            self._decisoes.fonte.value if self._decisoes.fonte is not None else ""
        )
        if fonte not in Fonte:
            recusar(MotivoDeDescarte.LINHA_QUEBRADA)
        return fonte

    def _ler_data(self, valores: dict[str, str], campo: str) -> date | None:
        bruto = valores.get(campo, "")
        if not bruto:
            return None
        data = interpretar_data(bruto, self._formato_barra)
        if data is not None:
            return data
        self.relatorio.datas_invalidas[campo] += 1
        if campo == "data_abertura":
            recusar(MotivoDeDescarte.SEM_DATA_DE_ABERTURA)
        if self._decisoes.datas_invalidas is PoliticaDeDatasInvalidas.DESCARTAR_LINHA:
            recusar(MotivoDeDescarte.DATA_INVALIDA)
        return None

    def _verificar_dado_pessoal(self, valores: dict[str, str]) -> None:
        if self._ja_normalizado:
            return
        for campo in CAMPOS_COM_TEXTO_LIVRE_DA_FONTE:
            valor = valores.get(campo)
            if valor and motivo_pelo_conteudo(valor) is not None:
                recusar(MotivoDeDescarte.DADO_PESSOAL)

    def _aplicar_correcoes(self, valores: dict[str, str], fonte: str) -> None:
        categoria = valores.get("categoria", "")
        if fonte == Fonte.CENTRAL_156 and categoria in CATEGORIAS_DO_156:
            valores["categoria"] = CATEGORIAS_DO_156[categoria]
            self.relatorio.correcoes[Correcao.CATEGORIA_UNIFICADA] += 1
        orgao = valores.get("orgao", "")
        if fonte == Fonte.OUVIDORIA and orgao in ORGAOS_DA_OUVIDORIA:
            valores["orgao"] = ORGAOS_DA_OUVIDORIA[orgao]
            self.relatorio.correcoes[Correcao.ORGAO_HARMONIZADO] += 1

    def _aplicar_decisao(self, valores: dict[str, str], campo: str, decisao: str) -> None:
        if decisao == DESCARTAR_LINHA:
            recusar(MotivoDeDescarte.VALOR_RECUSADO)
        if decisao == DEIXAR_VAZIO:
            valores[campo] = ""
        elif decisao != ACEITAR_COMO_NOVO:
            valores[campo] = decisao

    def _conferir_vocabulario(self, valores: dict[str, str], fonte: str) -> None:
        if self._plano.layout is CodigoDoLayout.FORMULARIO:
            return
        for campo in CAMPOS_VERIFICADOS_NO_VOCABULARIO:
            valor = valores.get(campo)
            conhecidos = self._referencias.vocabularios.get((fonte, campo))
            if not valor or not conhecidos or valor in conhecidos:
                continue
            decisao = decidir_valor(self._decisoes, campo, valor)
            if decisao is None:
                self.relatorio.valores_novos.setdefault(campo, Counter())[valor] += 1
                continue
            self._aplicar_decisao(valores, campo, decisao)

    def _resolver_id_local(self, valores: dict[str, str], fonte: str) -> str | None:
        if "id_local" in self._campos_mapeados:
            return valores.get("id_local") or None
        if ENDERECO not in self._campos_mapeados:
            return None
        if self._plano.sal is None:
            self.relatorio.sem_id_local += 1
            return None
        campos: tuple[str, ...] = (ENDERECO, NUMERO)
        if fonte == Fonte.DEFESA_CIVIL:
            campos = (ENDERECO, "bairro", AUXILIAR_LOCALIDADE)
        return gerar_id_local(tuple(valores.get(campo, "") for campo in campos), self._plano.sal)

    def _resolver_numero_informado(self, valores: dict[str, str]) -> bool | None:
        if "numero_informado" in self._campos_mapeados:
            return ler_booleano(valores.get("numero_informado", ""))
        if NUMERO in self._campos_mapeados:
            return numero_foi_informado(valores.get(NUMERO, ""))
        return None

    def _resolver_prazo(
        self, valores: dict[str, str], abertura: date, movimento: date | None
    ) -> PrazoResolvido:
        dias = None
        if "dias_ate_movimento" in self._campos_mapeados:
            dias = ler_inteiro(valores.get("dias_ate_movimento", ""))
        elif movimento is not None:
            dias = (movimento - abertura).days
        if dias is not None and dias < 0:
            self.relatorio.correcoes[Correcao.PRAZO_NEGATIVO] += 1
            return PrazoResolvido(None, negativo=True)
        return PrazoResolvido(dias, negativo=False)

    def _resolver_no_prazo(
        self, valores: dict[str, str], prazo: date | None, resposta: date | None
    ) -> bool | None:
        if "ouv_no_prazo" in self._campos_mapeados:
            return ler_booleano(valores.get("ouv_no_prazo", ""))
        if prazo is None:
            return None
        return resposta is not None and resposta <= prazo

    def _dias_da_camara(
        self, valores: dict[str, str], campo: str, datas: tuple[date, date | None]
    ) -> int | None:
        if campo in self._campos_mapeados:
            return ler_inteiro(valores.get(campo, ""))
        abertura, fim = datas
        return (fim - abertura).days if fim is not None else None

    def _gerar_chave(self, fonte: str, partes: dict[str, object], assinatura: int) -> int:
        if self._anotando:
            self._chaves.anotar(fonte, partes, assinatura)
            return 0
        chave = self._chaves.gerar(fonte, partes, assinatura)
        if not chave.repetida_no_arquivo:
            return chave.valor
        self.relatorio.repetidas_no_arquivo += 1
        if self._decisoes.repetidos_no_arquivo is PoliticaDeDuplicados.MANTER_UM:
            recusar(MotivoDeDescarte.REPETIDA_NO_ARQUIVO)
        return chave.valor

    def _montar_registro(self, celulas: Sequence[str]) -> RegistroDeDemanda:
        valores = self._ler_valores(celulas)
        self._adaptar(valores)
        fonte = self._identificar_fonte(valores)
        self._verificar_dado_pessoal(valores)
        datas = {campo: self._ler_data(valores, campo) for campo in CAMPOS_DE_DATA}
        abertura = datas["data_abertura"]
        if abertura is None:
            recusar(MotivoDeDescarte.SEM_DATA_DE_ABERTURA)
        self._aplicar_correcoes(valores, fonte)
        self._conferir_vocabulario(valores, fonte)
        territorio = self._territorio.resolver(valores, fonte)
        prazo = self._resolver_prazo(valores, abertura, datas["data_ult_movimento"])
        if fonte == Fonte.CENTRAL_156 and prazo.dias == 0:
            self.relatorio.correcoes[Correcao.FECHADO_NO_DIA] += 1
        self.relatorio.registrar_data(abertura)
        principal = self._conteudo_principal(valores, (fonte, abertura), datas, (territorio, prazo))
        complemento = self._conteudo_complementar(valores, abertura, datas)
        return self._registrar(valores, principal, complemento)

    def _conteudo_principal(
        self,
        valores: dict[str, str],
        origem: tuple[str, date],
        datas: dict[str, date | None],
        resolvidos: tuple[TerritorioResolvido, PrazoResolvido],
    ) -> tuple[object, ...]:
        fonte, abertura = origem
        territorio, prazo = resolvidos
        return (
            fonte,
            ler_inteiro(valores.get("ano", "")) or abertura.year,
            abertura,
            datas["data_ult_movimento"],
            prazo.dias,
            prazo.negativo,
            valores.get("categoria") or None,
            valores.get("servico_codigo") or None,
            valores.get("servico") or None,
            valores.get("tipo_registro") or None,
            valores.get("orgao") or None,
            valores.get("canal_entrada") or None,
            territorio.bairro,
            territorio.recuperado,
            self._territorio.resolver_rpa(valores, territorio.bairro),
            valores.get("situacao") or None,
            valores.get("iniciativa") or None,
        )

    def _conteudo_complementar(
        self, valores: dict[str, str], abertura: date, datas: dict[str, date | None]
    ) -> tuple[object, ...]:
        prazo_da_ouvidoria = datas["ouv_data_prazo"]
        envio = datas["camara_data_envio_prefeitura"]
        resposta = datas["camara_data_resposta"]
        return (
            prazo_da_ouvidoria,
            self._resolver_no_prazo(valores, prazo_da_ouvidoria, datas["data_ult_movimento"]),
            envio,
            valores.get("camara_canal_envio") or None,
            self._dias_da_camara(valores, "camara_dias_ate_envio", (abertura, envio)),
            resposta,
            self._dias_da_camara(valores, "camara_dias_ate_resposta", (abertura, resposta)),
            valores.get("camara_desfecho") or None,
        )

    def _registrar(
        self,
        valores: dict[str, str],
        principal: tuple[object, ...],
        complemento: tuple[object, ...],
    ) -> RegistroDeDemanda:
        fonte = str(principal[INDICE_DA_FONTE])
        ano_do_arquivo = self._ano_do_registro(valores)
        partes: dict[str, object] = {
            **valores,
            "ano_do_arquivo": ano_do_arquivo,
            "data_abertura": principal[INDICE_DA_ABERTURA],
            "data_ult_movimento": principal[INDICE_DO_MOVIMENTO],
            "bairro_oficial": principal[INDICE_DO_BAIRRO],
        }
        assinatura = calcular_hash("|".join(map(str, (*principal, *complemento))))
        return RegistroDeDemanda._make(
            (
                self._gerar_chave(fonte, partes, assinatura),
                assinatura,
                *principal,
                self._resolver_id_local(valores, fonte),
                self._resolver_numero_informado(valores),
                *complemento,
                valores.get("arquivo_origem") or self._plano.arquivo_origem,
                ano_do_arquivo,
            )
        )

    def _ano_do_registro(self, valores: dict[str, str]) -> int:
        origem = valores.get("arquivo_origem")
        if origem:
            return ano_do_nome_do_arquivo(origem) or self._ano_do_arquivo
        return self._ano_do_arquivo
