import { criarServicoDeAutenticacao } from '../../infrastructure/api/autenticacao'
import { criarServicoDaCidade } from '../../infrastructure/api/cidade'
import { ClienteHttp } from '../../infrastructure/api/cliente'
import { criarServicoDeContribuicoes } from '../../infrastructure/api/contribuicoes'
import {
  criarServicoDeEncaminhamentos,
  criarServicoDeRetornoDoOrgao,
} from '../../infrastructure/api/encaminhamentos'
import { criarServicoDeImportacoes } from '../../infrastructure/api/importacoes'
import { criarServicoDeInformacao } from '../../infrastructure/api/informacao'
import { criarServicoDoPainel } from '../../infrastructure/api/painel'

const URL_DA_API = import.meta.env.VITE_URL_DA_API ?? '/api/v1'

const cliente = new ClienteHttp(URL_DA_API)

export const servicoDeAutenticacao = criarServicoDeAutenticacao(cliente)
export const servicoDoPainel = criarServicoDoPainel(cliente)
export const servicoDeImportacoes = criarServicoDeImportacoes(cliente)
export const servicoDeContribuicoes = criarServicoDeContribuicoes(cliente)
export const servicoDaCidade = criarServicoDaCidade(cliente)
export const servicoDeEncaminhamentos = criarServicoDeEncaminhamentos(cliente)
export const servicoDeRetornoDoOrgao = criarServicoDeRetornoDoOrgao(cliente)
export const servicoDeInformacao = criarServicoDeInformacao(cliente)
