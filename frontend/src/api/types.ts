export interface Product {
  id: number
  offer_id: string
  name: string
  category: string
  price: string
  old_price: string | null
  stock: number
  source: string
}

export interface Stats {
  total: number
  avg_price: number
  total_stock: number
  by_category: { category: string; count: number; avg_price: number }[]
}

export interface PricePoint {
  price: number
  created_at: string
}
