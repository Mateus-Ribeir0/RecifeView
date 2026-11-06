import type {
  CatalogoDoFormulario,
  DecisaoDoPar,
  PaginaDeOcorrencias,
  ParParaRevisar,
  RelatoPreenchido,
  ResultadoDoEnvio,
  ResumoDasContribuicoes,
} from '../../domain/contribuicoes'
import type { ResumoDaImportacao } from '../../domain/importacoes'

export interface ServicoDeContribuicoes {
  catalogo(): Promise<CatalogoDoFormulario>
  logradouros(bairro: string): Promise<readonly string[]>
  enviar(relato: RelatoPreenchido): Promise<ResultadoDoEnvio>
  resumo(): Promise<ResumoDasContribuicoes>
  ocorrencias(deslocamento: number): Promise<PaginaDeOcorrencias>
  pares(): Promise<readonly ParParaRevisar[]>
  decidir(parId: number, decisao: DecisaoDoPar): Promise<void>
  gerarPacote(): Promise<ResumoDaImportacao>
}
