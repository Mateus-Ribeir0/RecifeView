import { useState } from 'react'

import capturaContribuicoes from '../../../assets/capturas/contribuicoes.webp'
import capturaInicio from '../../../assets/capturas/inicio.webp'
import capturaPrazos from '../../../assets/capturas/prazos.webp'
import capturaPrioridade from '../../../assets/capturas/prioridade.webp'
import capturaReincidencia from '../../../assets/capturas/reincidencia.webp'
import capturaRetorno from '../../../assets/capturas/retorno.webp'
import capturaTerritorio from '../../../assets/capturas/territorio.webp'
import capturaWarRoom from '../../../assets/capturas/war-room.webp'
import { Aparecer } from '../../../components/Aparecer'
import { Icone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { CabecalhoDaPagina } from '../CabecalhoDaPagina'
import { TELAS_DA_PLATAFORMA } from '../conteudo'
import secao from '../Secao.module.css'
import estilos from './PaginaPlataforma.module.css'

const CAPTURAS: Readonly<Record<string, string>> = {
  inicio: capturaInicio,
  'war-room': capturaWarRoom,
  retorno: capturaRetorno,
  reincidencia: capturaReincidencia,
  prazos: capturaPrazos,
  territorio: capturaTerritorio,
  prioridade: capturaPrioridade,
  contribuicoes: capturaContribuicoes,
}

export function PaginaPlataforma() {
  useTituloDaPagina('A plataforma')
  const [chave, definirChave] = useState(TELAS_DA_PLATAFORMA[0]?.chave)
  const tela = TELAS_DA_PLATAFORMA.find((item) => item.chave === chave) ?? TELAS_DA_PLATAFORMA[0]

  return (
    <>
      <CabecalhoDaPagina rotulo="A plataforma" titulo="Uma tela para cada pergunta da gestão">
        Cada tela começa pela pergunta que responde, informa a fonte, o período e o tamanho da
        amostra de cada número e funciona com os mesmos filtros.
      </CabecalhoDaPagina>
      <section className={secao.secao} aria-label="Telas do painel">
        <div className="conteudo">
          <div role="tablist" aria-label="Telas do painel" className={estilos.abas}>
            {TELAS_DA_PLATAFORMA.map(({ chave: chaveDaAba, nome, icone }) => (
              <button
                key={chaveDaAba}
                type="button"
                role="tab"
                id={`aba-${chaveDaAba}`}
                aria-selected={chaveDaAba === tela?.chave}
                aria-controls="tela-escolhida"
                className={estilos.aba}
                onClick={() => definirChave(chaveDaAba)}
              >
                <Icone nome={icone} tamanho={18} />
                {nome}
              </button>
            ))}
          </div>
          {tela && (
            <div
              key={tela.chave}
              id="tela-escolhida"
              role="tabpanel"
              aria-labelledby={`aba-${tela.chave}`}
              className={estilos.painel}
            >
              <div className={estilos.texto}>
                <h2 className={estilos.pergunta}>{tela.pergunta}</h2>
                <ul className={estilos.permite}>
                  {tela.permite.map((item) => (
                    <li key={item}>
                      <Icone nome="confirmado" tamanho={20} />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <figure className={estilos.moldura}>
                <img
                  src={CAPTURAS[tela.chave]}
                  width={1440}
                  height={900}
                  alt={`Tela ${tela.nome} do painel do RecifeView`}
                />
              </figure>
            </div>
          )}
          <p className={secao.nota}>
            Telas reais do painel, com a base de 07/10/2026. A tela de Contribuições mostra relatos
            de demonstração (dado fictício).
          </p>
        </div>
      </section>
      <section className={`${secao.secao} ${secao.fundoClaro}`} aria-labelledby="titulo-acesso">
        <div className={`conteudo ${estilos.acesso}`}>
          <Aparecer>
            <h2 id="titulo-acesso" className={secao.titulo}>
              Acesso restrito a gestores cadastrados
            </h2>
            <p className={secao.abertura}>
              Cada conta é criada pela administração. Os acessos e as consultas ficam registrados.
            </p>
          </Aparecer>
          <LinkDeBotao para="/entrar">Entrar no painel</LinkDeBotao>
        </div>
      </section>
    </>
  )
}
