import type { ResultadoDoEnvio } from '../../../../domain/contribuicoes'
import { Botao } from '../../../components/Botao'
import { Icone, type NomeDoIcone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import estilos from './ResultadoDoRelato.module.css'

interface Mensagem {
  icone: NomeDoIcone
  titulo: string
  texto: string
}

const MENSAGENS: Readonly<Record<ResultadoDoEnvio, Mensagem>> = {
  nova: {
    icone: 'confirmado',
    titulo: 'Relato recebido',
    texto:
      'Ele entrou na fila de revisão da gestão. Depois de revisado, passa a contar nos indicadores do bairro e do serviço.',
  },
  somada: {
    icone: 'somar',
    titulo: 'Outra pessoa já relatou este problema',
    texto:
      'O seu relato foi somado ao anterior. A ocorrência continua sendo uma só, agora com mais gente apontando para ela.',
  },
  em_conferencia: {
    icone: 'pessoas',
    titulo: 'Recebido, e parece com outro relato',
    texto:
      'A gestão vai conferir se é o mesmo problema. Se for, os relatos viram uma ocorrência só. Se não for, os dois seguem separados.',
  },
}

interface Propriedades {
  resultado: ResultadoDoEnvio
  aoRecomecar: () => void
}

export function ResultadoDoRelato({ resultado, aoRecomecar }: Propriedades) {
  const { icone, titulo, texto } = MENSAGENS[resultado]

  return (
    <section className={estilos.cartao} role="status">
      <span className={estilos.icone}>
        <Icone nome={icone} tamanho={36} />
      </span>
      <h2 className={estilos.titulo}>{titulo}</h2>
      <p className={estilos.texto}>{texto}</p>
      <p className={estilos.lembrete}>
        Este relato não gera protocolo. Para acompanhar um pedido de serviço, use a Central 156.
      </p>
      <div className={estilos.acoes}>
        <Botao type="button" onClick={aoRecomecar}>
          Enviar outro relato
        </Botao>
        <LinkDeBotao para="/dados-e-confianca" variante="secundario">
          Como a duplicidade é evitada
        </LinkDeBotao>
      </div>
    </section>
  )
}
