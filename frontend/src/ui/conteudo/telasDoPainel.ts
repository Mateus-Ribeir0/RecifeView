export interface TelaDoPainel {
  nome: string
  mostra: string
}

export const TELAS_DO_PAINEL: readonly TelaDoPainel[] = [
  { nome: 'Visão geral', mostra: 'Os principais indicadores e alertas do período escolhido.' },
  {
    nome: 'Mapa por bairro e RPA',
    mostra: 'Demanda por mil habitantes e reincidência em cada um dos 94 bairros.',
  },
  { nome: 'Prazos', mostra: 'Mediana e percentil 90 do atendimento por serviço e por órgão.' },
  { nome: 'Recorrências', mostra: 'Onde o mesmo problema volta e onde há só pedido duplicado.' },
  {
    nome: 'Fluxo Câmara → Prefeitura',
    mostra: 'Quantas indicações saem, chegam e recebem resposta, e em quanto tempo.',
  },
]
