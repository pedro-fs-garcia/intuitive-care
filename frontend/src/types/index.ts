export interface Operadora {
  cnpj: string
  razao_social: string
  registro_ans: string | null
  modalidade: string | null
  uf: string
}

export interface Despesa {
  trimestre: number
  ano: number
  valor_despesa: number  // Valor isolado do trimestre (desacumulado)
  valor_ytd?: number     // Valor acumulado YTD (Year-to-Date)
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface DespesasResponse extends PaginatedResponse<Despesa> {
  operadora: {
    cnpj: string
    razao_social: string
  }
}

export interface DespesaPorUF {
  uf: string
  total: number
  media_trimestral: number
  qtd_operadoras: number
}

export interface TopOperadora {
  cnpj: string
  razao_social: string
  uf: string
  total_despesas: number
}

export interface Estatisticas {
  resumo: {
    total_despesas: number
    media_despesas: number
    total_registros: number
  }
  top_5_operadoras: TopOperadora[]
  despesas_por_uf: DespesaPorUF[]
}

export interface OperadoraCrescimento {
  cnpj: string
  razao_social: string
  despesa_inicial: number
  despesa_final: number
  crescimento_percentual: number
}

export interface UFDistribuicao {
  uf: string
  qtd_operadoras: number
  total_despesas: number
  media_por_registro: number
  media_por_operadora: number
}

export interface EstatisticasComplementares {
  top_5_crescimento: OperadoraCrescimento[]
  top_5_uf: UFDistribuicao[]
  operadoras_acima_media: {
    total: number
    media_geral_referencia: number
    criterio: string
  }
}
