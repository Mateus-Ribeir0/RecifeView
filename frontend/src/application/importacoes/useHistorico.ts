import { useCallback, useEffect, useState } from 'react'

import {
  estaEmProcessamento,
  type CampoDaBase,
  type FiltroDoHistorico,
  type PaginaDeImportacoes,
  type PaginaDeRegistros,
} from '../../domain/importacoes'
import { useServicoDeImportacoes } from './contexto'

const INTERVALO_DE_ATUALIZACAO_EM_MS = 3000

interface EstadoDoHistorico {
  pagina: PaginaDeImportacoes | null
  erro: unknown
}

export function useHistorico(
  filtro: FiltroDoHistorico,
): EstadoDoHistorico & { recarregar: () => void } {
  const servico = useServicoDeImportacoes()
  const [estado, definirEstado] = useState<EstadoDoHistorico>({ pagina: null, erro: null })
  const [versao, definirVersao] = useState(0)
  const recarregar = useCallback(() => definirVersao((atual) => atual + 1), [])

  useEffect(() => {
    let ativo = true
    let temporizador: ReturnType<typeof setTimeout> | undefined

    async function atualizar() {
      try {
        const pagina = await servico.listar(filtro)
        if (!ativo) return
        definirEstado({ pagina, erro: null })
        if (pagina.itens.some((item) => estaEmProcessamento(item.status))) {
          temporizador = setTimeout(atualizar, INTERVALO_DE_ATUALIZACAO_EM_MS)
        }
      } catch (erro) {
        if (ativo) definirEstado((atual) => ({ ...atual, erro }))
      }
    }

    void atualizar()
    return () => {
      ativo = false
      clearTimeout(temporizador)
    }
  }, [servico, filtro, versao])

  return { ...estado, recarregar }
}

export function useCamposDaBase(): readonly CampoDaBase[] {
  const servico = useServicoDeImportacoes()
  const [campos, definirCampos] = useState<readonly CampoDaBase[]>([])

  useEffect(() => {
    let ativo = true
    void servico.campos().then((lista) => {
      if (ativo) definirCampos(lista)
    })
    return () => {
      ativo = false
    }
  }, [servico])

  return campos
}

export function useRegistrosImportados(id: number, deslocamento: number): PaginaDeRegistros | null {
  const servico = useServicoDeImportacoes()
  const [pagina, definirPagina] = useState<PaginaDeRegistros | null>(null)

  useEffect(() => {
    let ativo = true
    void servico.registros(id, deslocamento).then((resultado) => {
      if (ativo) definirPagina(resultado)
    })
    return () => {
      ativo = false
    }
  }, [servico, id, deslocamento])

  return pagina
}
