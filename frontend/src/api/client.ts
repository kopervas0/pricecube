import type { Product, Stats } from './types'

const BASE = '/api'

async function get<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json()
}

export async function fetchProducts(params: { category?: string; search?: string; page?: number } = {}): Promise<{ count: number; results: Product[] }> {
  const qs = new URLSearchParams()
  if (params.category) qs.set('category', params.category)
  if (params.search) qs.set('search', params.search)
  if (params.page) qs.set('page', String(params.page))
  return get(`${BASE}/products/?${qs.toString()}`)
}

export async function fetchStats(): Promise<Stats> {
  return get(`${BASE}/products/stats/`)
}

export async function triggerSync(): Promise<{ result: unknown }> {
  const res = await fetch(`${BASE}/products/sync/`, { method: 'POST' })
  if (!res.ok) throw new Error(`sync error ${res.status}`)
  return res.json()
}
