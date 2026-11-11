import { useId, useState } from 'react'
import { Link } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'
import { Botao } from '../../components/Botao'
import campo from '../../components/Campo.module.css'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './Cidade.module.css'
import { ComparacaoDoBairro } from './ComparacaoDoBairro'

export function PaginaMeuBairro() {
  useTituloDaPagina('Meu bairro')
  const { estado, atualizarConta } = useSessao()
  const usuario = estado.situacao === 'autenticada' ? estado.usuario : null
  const [bairro, definirBairro] = useState(usuario?.bairroOficial ?? '')
  const [salvo, definirSalvo] = useState(false)
  const { catalogo } = useCatalogoDoFormulario()
  const idDoBairro = useId()
  const nome = catalogo?.bairros.find((item) => item.chave === bairro)?.nome
  const podeSalvar = Boolean(usuario && bairro && bairro !== usuario.bairroOficial)

  async function salvar() {
    if (!usuario) return
    await atualizarConta({ nome: usuario.nome, bairroOficial: bairro })
    definirSalvo(true)
  }

  return (
    <>
      <h1 className={estilos.titulo}>{nome ? `Meu bairro: ${nome}` : 'Meu bairro'}</h1>
      {!bairro && (
        <p className={estilos.subtitulo}>
          Escolha um bairro para ver como ele se compara com o Recife nos dados abertos.
        </p>
      )}
      <div className={estilos.escolhaDoBairro}>
        <div className={campo.campo}>
          <label htmlFor={idDoBairro} className={campo.rotulo}>
            Bairro
          </label>
          <select
            id={idDoBairro}
            className={campo.entrada}
            value={bairro}
            onChange={(evento) => {
              definirBairro(evento.target.value)
              definirSalvo(false)
            }}
          >
            <option value="">Escolha</option>
            {catalogo?.bairros.map(({ chave, nome: rotulo }) => (
              <option key={chave} value={chave}>
                {rotulo}
              </option>
            ))}
          </select>
        </div>
        {podeSalvar && (
          <Botao variante="secundario" onClick={() => void salvar()}>
            Salvar como meu bairro
          </Botao>
        )}
        {salvo && <span role="status">Bairro salvo na sua conta.</span>}
      </div>
      {bairro && (
        <ComparacaoDoBairro
          bairro={bairro}
          acao={(dados) => (
            <Link to={`/cidade?bairro=${encodeURIComponent(dados.bairroOficial)}`}>
              Ver os relatos de {dados.nome}
            </Link>
          )}
        />
      )}
    </>
  )
}
