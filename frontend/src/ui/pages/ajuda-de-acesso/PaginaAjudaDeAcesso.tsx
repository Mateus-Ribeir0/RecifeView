import { Link } from 'react-router'

import { MINUTOS_DE_BLOQUEIO, TENTATIVAS_ANTES_DO_BLOQUEIO } from '../../../domain/acesso'
import acesso from '../../components/Acesso.module.css'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './PaginaAjudaDeAcesso.module.css'

const DUVIDAS = [
  {
    pergunta: 'Esqueci a senha',
    resposta:
      'Peça à administração do RecifeView uma senha temporária. No primeiro acesso com ela, você define uma senha nova.',
  },
  {
    pergunta: 'A conta foi bloqueada',
    resposta: `Depois de ${TENTATIVAS_ANTES_DO_BLOQUEIO} tentativas erradas seguidas, a conta fica bloqueada por ${MINUTOS_DE_BLOQUEIO} minutos. Espere esse tempo e tente de novo.`,
  },
  {
    pergunta: 'Ainda não tenho acesso',
    resposta:
      'Não há cadastro aberto. Peça a inclusão à administração do RecifeView, informando o seu e-mail institucional.',
  },
  {
    pergunta: 'Apareceu “conta desativada”',
    resposta: 'A administração desativou a conta. Fale com ela para saber o motivo e reativar.',
  },
] as const

export function PaginaAjudaDeAcesso() {
  useTituloDaPagina('Não consegue entrar?')

  return (
    <LayoutDeAcesso>
      <h1 className={acesso.titulo}>Não consegue entrar?</h1>
      <p className={acesso.subtitulo}>
        As contas do RecifeView são criadas pela administração do projeto, para gestores públicos.
      </p>
      <dl className={estilos.duvidas}>
        {DUVIDAS.map(({ pergunta, resposta }) => (
          <div key={pergunta}>
            <dt>{pergunta}</dt>
            <dd>{resposta}</dd>
          </div>
        ))}
      </dl>
      <div className={acesso.links}>
        <Link to="/entrar">Voltar para a tela de entrada</Link>
      </div>
    </LayoutDeAcesso>
  )
}
