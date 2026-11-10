import { Link } from 'react-router'

import { Aparecer } from '../../../components/Aparecer'
import { Icone, type NomeDoIcone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import estilos from './ChamadaFinal.module.css'

interface Caminho {
  icone: NomeDoIcone
  titulo: string
  texto: string
  para: string
  acao: string
}

const CAMINHOS: readonly Caminho[] = [
  {
    icone: 'pessoas',
    titulo: 'Fiscalize junto',
    texto:
      'Crie uma conta para ver o que já foi relatado perto de você e acompanhar cada caso até ele entrar nos números da gestão.',
    para: '/cadastrar',
    acao: 'Criar conta',
  },
  {
    icone: 'relato',
    titulo: 'Viu um problema agora?',
    texto:
      'Relate em um minuto, sem se identificar. Se outra pessoa já relatou, o seu relato reforça o mesmo caso.',
    para: '/contribuir',
    acao: 'Relatar um problema',
  },
]

export function ChamadaFinal() {
  return (
    <>
      <section className={estilos.chamada} aria-label="Por onde continuar">
        <div className={`conteudo ${estilos.grade}`}>
          {CAMINHOS.map(({ icone, titulo, texto, para, acao }, indice) => (
            <Aparecer key={para} atraso={indice * 120}>
              <span className={estilos.icone}>
                <Icone nome={icone} tamanho={28} />
              </span>
              <h2 className={estilos.titulo}>{titulo}</h2>
              <p className={estilos.texto}>{texto}</p>
              <LinkDeBotao para={para} variante="claro">
                {acao}
              </LinkDeBotao>
            </Aparecer>
          ))}
        </div>
      </section>
      <div className={estilos.gestao}>
        <div className="conteudo">
          <p>
            Trabalha na gestão pública do Recife?{' '}
            <Link to="/entrar/gestao">Entre pela área da gestão</Link> para ver o painel, revisar os
            relatos e importar arquivos.
          </p>
        </div>
      </div>
    </>
  )
}
