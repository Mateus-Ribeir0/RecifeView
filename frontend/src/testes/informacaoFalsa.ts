import { vi } from 'vitest'

import type { ServicoDeInformacao } from '../application/informacao/servico'
import type { AndamentoDoPedido, PedidoAcompanhado } from '../domain/pedidos'

export const ANDAMENTO: AndamentoDoPedido = {
  fonte: 'OUVIDORIA',
  rotuloDaFonte: 'Ouvidoria',
  protocolo: 'TESTE-0001',
  dataAbertura: '2026-09-01',
  categoria: 'ILUMINACAO',
  servico: 'LAMPADA APAGADA',
  tipoRegistro: 'RECLAMACAO',
  orgao: 'EMLURB',
  situacao: 'EM ANDAMENTO',
  dataUltMovimento: '2026-09-10',
  prazoDaFonte: '2026-10-01',
  bairroOficial: null,
  rpa: null,
  encaminhamentos: [
    {
      codigo: 'ENC-2026-000001',
      orgao: 'NEOENERGIA',
      nomeDoOrgao: 'Neoenergia Pernambuco',
      situacao: 'recebido',
      atrasado: false,
      encaminhadoEm: '2026-11-11T15:00:00Z',
      prazoDeResposta: '2026-12-11',
      protocoloDoOrgao: 'NEO-77',
      etapas: [
        { situacao: 'enviado', ocorridoEm: '2026-11-11T15:00:00Z' },
        { situacao: 'recebido', ocorridoEm: '2026-11-12T10:00:00Z' },
      ],
    },
  ],
}

export const PEDIDO: PedidoAcompanhado = {
  id: 3,
  protocolo: 'TESTE-0001',
  criadoEm: '2026-11-11T15:00:00Z',
  andamentos: [ANDAMENTO],
}

export function criarInformacaoFalsa(
  substituicoes: Partial<ServicoDeInformacao> = {},
): ServicoDeInformacao {
  return {
    consultarPedido: vi.fn().mockResolvedValue([ANDAMENTO]),
    indicadoresDoBairro: vi.fn().mockRejectedValue(new Error('não usado')),
    meusPedidos: vi.fn().mockResolvedValue([PEDIDO]),
    acompanharPedido: vi.fn().mockResolvedValue(PEDIDO),
    deixarDeAcompanhar: vi.fn().mockResolvedValue(undefined),
    ...substituicoes,
  }
}
