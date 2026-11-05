import { useState } from 'react'

import { useServicoDeImportacoes } from '../../../application/importacoes/contexto'
import { contar } from '../../../domain/formatacao'
import type { DetalheDaImportacao, Pendencia } from '../../../domain/importacoes'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Importacoes.module.css'
import { PerguntaDeEscolha } from './PerguntaDeEscolha'
import { ValoresEmDuvida } from './ValoresEmDuvida'

type Substituicoes = Record<string, Record<string, string>>

function sugestoesIniciais(itens: readonly Pendencia[]): Substituicoes {
  const inicial: Substituicoes = {}
  itens.forEach(({ campo, valores }) => {
    if (!campo) return
    inicial[campo] = Object.fromEntries(
      valores.flatMap(({ valor, sugestao }) => (sugestao ? [[valor, sugestao]] : [])),
    )
  })
  return inicial
}

function semEscolhasVazias(substituicoes: Substituicoes): Substituicoes {
  return Object.fromEntries(
    Object.entries(substituicoes).map(([campo, valores]) => [
      campo,
      Object.fromEntries(Object.entries(valores).filter(([, escolha]) => escolha)),
    ]),
  )
}

interface Propriedades {
  importacao: DetalheDaImportacao
  aoConcluir: () => void
  aoCancelar: () => void
}

export function PassoPendencias({ importacao, aoConcluir, aoCancelar }: Propriedades) {
  const servico = useServicoDeImportacoes()
  const { itens } = importacao.pendencias
  const [substituicoes, definirSubstituicoes] = useState<Substituicoes>(() =>
    sugestoesIniciais(itens),
  )
  const [padroes, definirPadroes] = useState<Record<string, string>>({})
  const [respostas, definirRespostas] = useState<Record<string, string>>({})
  const [enviando, definirEnviando] = useState(false)
  const [erro, definirErro] = useState<unknown>(null)

  function responder(chave: string, valor: string) {
    definirRespostas((atuais) => ({ ...atuais, [chave]: valor }))
  }

  async function aplicar() {
    definirEnviando(true)
    definirErro(null)
    try {
      await servico.responderPendencias(importacao.id, {
        ...respostas,
        substituicoes: semEscolhasVazias(substituicoes),
        padraoParaValores: Object.fromEntries(
          Object.entries(padroes).filter(([, escolha]) => escolha),
        ),
      })
      aoConcluir()
    } catch (falha) {
      definirErro(falha)
      definirEnviando(false)
    }
  }

  function desenhar(pendencia: Pendencia) {
    const { tipo, campo, quantidade, detalhes } = pendencia
    if (tipo === 'bairro_desconhecido' || tipo === 'valor_novo') {
      const nome = campo ?? ''
      return (
        <ValoresEmDuvida
          key={`${tipo}-${nome}`}
          pendencia={pendencia}
          escolhas={substituicoes[nome] ?? {}}
          padrao={padroes[nome] ?? ''}
          aoEscolher={(valor, escolha) =>
            definirSubstituicoes((atuais) => ({
              ...atuais,
              [nome]: { ...atuais[nome], [valor]: escolha },
            }))
          }
          aoEscolherPadrao={(escolha) =>
            definirPadroes((atuais) => ({ ...atuais, [nome]: escolha }))
          }
        />
      )
    }
    if (tipo === 'formato_de_data') {
      return (
        <PerguntaDeEscolha
          key={tipo}
          titulo="As datas estão em que ordem?"
          nome="formato-de-data"
          valor={respostas.formatoDeData}
          aoEscolher={(valor) => responder('formatoDeData', valor)}
          opcoes={[
            { valor: 'dia_mes_ano', rotulo: 'Dia, mês e ano (31/12/2026)' },
            { valor: 'mes_dia_ano', rotulo: 'Mês, dia e ano (12/31/2026)' },
          ]}
        >
          <p className={estilos.textoDaPergunta}>
            Nenhuma data do arquivo tem dia acima de 12, então não dá para saber sozinho.
          </p>
        </PerguntaDeEscolha>
      )
    }
    if (tipo === 'datas_invalidas') {
      return (
        <PerguntaDeEscolha
          key={tipo}
          titulo={contar(quantidade, 'data não pôde ser lida', 'datas não puderam ser lidas')}
          nome="datas-invalidas"
          valor={respostas.datasInvalidas}
          aoEscolher={(valor) => responder('datasInvalidas', valor)}
          opcoes={[
            { valor: 'deixar_vazia', rotulo: 'Manter a linha e deixar a data vazia' },
            { valor: 'descartar_linha', rotulo: 'Descartar as linhas com data inválida' },
          ]}
        />
      )
    }
    if (tipo === 'repetidos_na_base') {
      return (
        <PerguntaDeEscolha
          key={tipo}
          titulo={`${contar(quantidade, 'registro já existe', 'registros já existem')} na base com outros dados`}
          nome="repetidos-na-base"
          valor={respostas.repetidosNaBase}
          aoEscolher={(valor) => responder('repetidosNaBase', valor)}
          opcoes={[
            {
              valor: 'atualizar',
              rotulo: 'Atualizar com a versão deste arquivo',
              detalhe: 'O mais comum: cada arquivo novo traz a situação mais recente.',
            },
            { valor: 'manter_atuais', rotulo: 'Manter os dados atuais e ignorar estes' },
            {
              valor: 'inserir_como_novos',
              rotulo: 'Entrar como registros novos',
              detalhe: 'Use só se tiver certeza de que são pedidos diferentes.',
            },
          ]}
        >
          <p className={estilos.textoDaPergunta}>
            Idênticos à base, sem mudança: {contar(detalhes.iguais ?? 0, 'registro', 'registros')}.
          </p>
        </PerguntaDeEscolha>
      )
    }
    return (
      <PerguntaDeEscolha
        key={tipo}
        titulo={`${contar(quantidade, 'linha tem', 'linhas têm')} o mesmo conteúdo de outra linha do arquivo`}
        nome="repetidos-no-arquivo"
        valor={respostas.repetidosNoArquivo}
        aoEscolher={(valor) => responder('repetidosNoArquivo', valor)}
        opcoes={[
          {
            valor: 'manter_todos',
            rotulo: 'Manter todas',
            detalhe:
              'Podem ser pedidos diferentes no mesmo dia e lugar. É o que o pipeline do grupo faz.',
          },
          { valor: 'manter_um', rotulo: 'Manter só uma de cada' },
        ]}
      />
    )
  }

  return (
    <section className={estilos.passo} aria-labelledby="titulo-das-decisoes">
      <h2 id="titulo-das-decisoes">O que não bateu</h2>
      <p className={estilos.subtitulo}>
        Nada foi gravado ainda. Decida o caminho de cada item; depois o arquivo é conferido de novo.
      </p>
      {itens.map(desenhar)}
      {erro ? (
        <Aviso tipo="erro" titulo="As decisões não foram salvas">
          {mensagemDeFalha(erro)}
        </Aviso>
      ) : null}
      <div className={estilos.acoes}>
        <Botao compacto disabled={enviando} onClick={() => void aplicar()}>
          {enviando ? 'Aplicando...' : 'Aplicar decisões'}
        </Botao>
        <Botao variante="secundario" compacto onClick={aoCancelar}>
          Cancelar importação
        </Botao>
      </div>
    </section>
  )
}
