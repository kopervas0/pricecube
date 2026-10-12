import { useCallback, useEffect, useState } from 'react'
import { fetchProducts, fetchStats, triggerSync } from './api/client'
import type { Product, Stats } from './api/types'

export default function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [p, s] = await Promise.all([
        fetchProducts({ search, category }),
        fetchStats(),
      ])
      setProducts(p.results)
      setStats(s)
    } catch {
      setError('Не удалось загрузить данные API')
    } finally {
      setLoading(false)
    }
  }, [search, category])

  useEffect(() => {
    void load()
  }, [load])

  const handleSync = async () => {
    setSyncing(true)
    try {
      await triggerSync()
      await load()
    } catch {
      setError('Синхронизация не удалась')
    } finally {
      setSyncing(false)
    }
  }

  const isDemo = stats ? (products[0]?.source ?? 'demo') === 'demo' : true
  const categories = stats?.by_category.map((c) => c.category) ?? []

  return (
    <div className="container">
      <div className="header">
        <h1>PriceCube · Аналитика маркетплейса</h1>
        <span className={`badge ${isDemo ? 'demo' : 'ozon'}`}>
          {isDemo ? 'демо-режим (нет товаров в магазине)' : 'Ozon API'}
        </span>
      </div>

      <div className="stats">
        <div className="stat">
          <div className="label">Товаров</div>
          <div className="value">{stats?.total ?? '—'}</div>
        </div>
        <div className="stat">
          <div className="label">Средняя цена</div>
          <div className="value">{stats ? `${Math.round(stats.avg_price)} ₽` : '—'}</div>
        </div>
        <div className="stat">
          <div className="label">Остаток, шт</div>
          <div className="value">{stats?.total_stock ?? '—'}</div>
        </div>
        <div className="stat">
          <div className="label">Категорий</div>
          <div className="value">{stats?.by_category.length ?? '—'}</div>
        </div>
      </div>

      <div className="toolbar">
        <input
          placeholder="Поиск по названию…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">Все категории</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <button onClick={() => void load()}>Обновить</button>
        <button onClick={() => void handleSync()} disabled={syncing}>
          {syncing ? 'Синхронизация…' : 'Синхронизировать'}
        </button>
      </div>

      {error && <div className="empty" style={{ color: 'var(--danger)' }}>{error}</div>}

      {loading ? (
        <div className="empty">Загрузка…</div>
      ) : products.length === 0 ? (
        <div className="empty">Товары не найдены</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Артикул</th>
              <th>Название</th>
              <th>Категория</th>
              <th>Цена</th>
              <th>Остаток</th>
              <th>Источник</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id}>
                <td className="dim">{p.offer_id}</td>
                <td>{p.name}</td>
                <td className="dim">{p.category}</td>
                <td className="price">
                  {Number(p.price).toLocaleString('ru-RU')} ₽
                  {p.old_price && (
                    <span className="dim" style={{ marginLeft: 8, textDecoration: 'line-through' }}>
                      {Number(p.old_price).toLocaleString('ru-RU')}
                    </span>
                  )}
                </td>
                <td className="stock">{p.stock}</td>
                <td className="dim">{p.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {stats && stats.by_category.length > 0 && (
        <div className="chart">
          <h3>Товары по категориям</h3>
          <div className="bars">
            {stats.by_category.map((c) => {
              const max = Math.max(...stats.by_category.map((x) => x.count))
              const height = Math.round((c.count / max) * 140) + 8
              return (
                <div className="bar" key={c.category}>
                  <span className="num">{c.count}</span>
                  <div className="fill" style={{ height }} />
                  <span className="name">{c.category}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
