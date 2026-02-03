import axios, { type AxiosInstance } from 'axios'
import type {
  Operadora,
  PaginatedResponse,
  DespesasResponse,
  Estatisticas,
  EstatisticasComplementares
} from '../types'

const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

export async function fetchOperadoras(
  page: number = 1,
  limit: number = 10,
  search: string = ''
): Promise<PaginatedResponse<Operadora>> {
  const params: Record<string, string | number> = { page, limit }
  if (search) params.search = search
  const response = await api.get<PaginatedResponse<Operadora>>('/operadoras', { params })
  return response.data
}

export async function fetchOperadora(cnpj: string): Promise<Operadora> {
  const response = await api.get<Operadora>(`/operadoras/${cnpj}`)
  return response.data
}

export async function fetchOperadoraDespesas(
  cnpj: string,
  page: number = 1,
  limit: number = 10
): Promise<DespesasResponse> {
  const response = await api.get<DespesasResponse>(`/operadoras/${cnpj}/despesas`, {
    params: { page, limit }
  })
  return response.data
}

export async function fetchEstatisticas(): Promise<Estatisticas> {
  const response = await api.get<Estatisticas>('/estatisticas')
  return response.data
}

export async function fetchEstatisticasComplementares(): Promise<EstatisticasComplementares> {
  const response = await api.get<EstatisticasComplementares>('/estatisticas-complementares')
  return response.data
}

export default api
