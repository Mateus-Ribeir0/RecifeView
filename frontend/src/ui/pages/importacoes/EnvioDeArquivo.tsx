import { useRef, useState, type DragEvent } from 'react'
import { useNavigate } from 'react-router'

import { useServicoDeImportacoes } from '../../../application/importacoes/contexto'
import { formatarTamanho } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Importacoes.module.css'

const FORMATOS_ACEITOS = '.csv,.tsv,.txt,.json,.xlsx,.zip,.gz,.xz'

export function EnvioDeArquivo() {
  const servico = useServicoDeImportacoes()
  const navegar = useNavigate()
  const entrada = useRef<HTMLInputElement>(null)
  const [arquivo, definirArquivo] = useState<File | null>(null)
  const [enviando, definirEnviando] = useState(false)
  const [sobre, definirSobre] = useState(false)
  const [erro, definirErro] = useState<unknown>(null)

  function receberSoltura(evento: DragEvent) {
    evento.preventDefault()
    definirSobre(false)
    const solto = evento.dataTransfer.files[0]
    if (solto) definirArquivo(solto)
  }

  async function enviar() {
    if (!arquivo) return
    definirEnviando(true)
    definirErro(null)
    try {
      const importacao = await servico.enviar(arquivo)
      await navegar(`/painel/importacoes/${importacao.id}`)
    } catch (falha) {
      definirErro(falha)
      definirEnviando(false)
    }
  }

  return (
    <>
      <div
        className={`${estilos.soltura} ${sobre ? estilos.solturaAtiva : ''}`}
        onDragOver={(evento) => {
          evento.preventDefault()
          definirSobre(true)
        }}
        onDragLeave={() => definirSobre(false)}
        onDrop={receberSoltura}
      >
        <p className={estilos.solturaTitulo}>
          {arquivo ? arquivo.name : 'Arraste o arquivo para cá'}
        </p>
        <p className={estilos.solturaTexto}>
          {arquivo
            ? formatarTamanho(arquivo.size)
            : 'CSV, TSV, JSON ou XLSX, soltos ou dentro de ZIP, GZ ou XZ.'}
        </p>
        <input
          ref={entrada}
          type="file"
          accept={FORMATOS_ACEITOS}
          className="visualmente-oculto"
          aria-label="Escolher arquivo"
          onChange={(evento) => definirArquivo(evento.target.files?.[0] ?? null)}
        />
        <div className={estilos.acoes}>
          <Botao variante="secundario" compacto onClick={() => entrada.current?.click()}>
            {arquivo ? 'Trocar arquivo' : 'Escolher arquivo'}
          </Botao>
          {arquivo && (
            <Botao compacto disabled={enviando} onClick={() => void enviar()}>
              {enviando ? 'Enviando...' : 'Enviar e analisar'}
            </Botao>
          )}
        </div>
      </div>
      {erro ? (
        <Aviso tipo="erro" titulo="O arquivo não foi enviado">
          {mensagemDeFalha(erro)}
        </Aviso>
      ) : null}
    </>
  )
}
