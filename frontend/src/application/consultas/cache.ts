const LIMITE_DE_ENTRADAS = 80

export type EstadoDaEntrada<T> =
  | { situacao: 'carregando' }
  | { situacao: 'pronta'; dados: T }
  | { situacao: 'erro'; erro: unknown }

type Ouvinte = () => void

/** Guarda as respostas por chave e avisa quem está olhando quando uma delas muda. */
export class CacheDeConsultas {
  private readonly entradas = new Map<string, EstadoDaEntrada<unknown>>()
  private readonly ultimasProntas = new Map<string, unknown>()
  private readonly ouvintes = new Set<Ouvinte>()

  assinar = (ouvinte: Ouvinte): (() => void) => {
    this.ouvintes.add(ouvinte)
    return () => this.ouvintes.delete(ouvinte)
  }

  ler<T>(chave: string): EstadoDaEntrada<T> | undefined {
    return this.entradas.get(chave) as EstadoDaEntrada<T> | undefined
  }

  ultimaPronta<T>(grupo: string): T | undefined {
    return this.ultimasProntas.get(grupo) as T | undefined
  }

  garantir<T>(grupo: string, chave: string, buscar: () => Promise<T>): void {
    if (this.entradas.has(chave)) return
    this.iniciar(grupo, chave, buscar)
  }

  recarregar<T>(grupo: string, chave: string, buscar: () => Promise<T>): void {
    this.iniciar(grupo, chave, buscar)
  }

  esquecerTudo(): void {
    this.entradas.clear()
    this.ultimasProntas.clear()
    this.avisar()
  }

  private iniciar<T>(grupo: string, chave: string, buscar: () => Promise<T>): void {
    this.gravar(chave, { situacao: 'carregando' })
    buscar().then(
      (dados) => {
        this.ultimasProntas.set(grupo, dados)
        this.gravar(chave, { situacao: 'pronta', dados })
      },
      (erro: unknown) => this.gravar(chave, { situacao: 'erro', erro }),
    )
  }

  private gravar(chave: string, estado: EstadoDaEntrada<unknown>): void {
    this.entradas.delete(chave)
    this.entradas.set(chave, estado)
    if (this.entradas.size > LIMITE_DE_ENTRADAS) {
      const maisAntiga = this.entradas.keys().next().value
      if (maisAntiga !== undefined) this.entradas.delete(maisAntiga)
    }
    this.avisar()
  }

  private avisar(): void {
    this.ouvintes.forEach((ouvinte) => ouvinte())
  }
}
