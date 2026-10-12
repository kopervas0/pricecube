import { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import { exportHistoryUrl, fetchHistory } from '../api/client'
import type { PricePoint, Product } from '../api/types'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
)

interface Props {
  product: Product
  onClose: () => void
}

function fmtDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })
}

export default function ProductModal({ product, onClose }: Props) {
  const [history, setHistory] = useState<PricePoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError('')
    fetchHistory(product.id)
      .then((data) => {
        if (alive) setHistory(data)
      })
      .catch(() => {
        if (alive) setError('Не удалось загрузить историю цен')
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [product.id])

  // закрытие по Escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const labels = history.map((h) => fmtDate(h.created_at))
  const prices = history.map((h) => Number(h.price))
  const chartData = {
    labels,
    datasets: [
      {
        label: 'Цена, ₽',
        data: prices,
        borderColor: '#4c8dff',
        backgroundColor: 'rgba(76, 141, 255, 0.15)',
        fill: true,
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: '#4c8dff',
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#8b96ad' } },
      title: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx: unknown) => {
            const v = (ctx as { parsed: { y: number } }).parsed.y
            return `${v.toLocaleString('ru-RU')} ₽`
          },
        },
      },
    },
    scales: {
      x: { ticks: { color: '#8b96ad' }, grid: { color: '#2a3346' } },
      y: {
        ticks: {
          color: '#8b96ad',
          callback: (v: unknown) => `${Number(v).toLocaleString('ru-RU')} ₽`,
        },
        grid: { color: '#2a3346' },
      },
    },
  }

  const hasOld = product.old_price && Number(product.old_price) > Number(product.price)
  const min = prices.length ? Math.min(...prices) : 0
  const max = prices.length ? Math.max(...prices) : 0

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <div className="modal-title">{product.name}</div>
            <div className="modal-sub dim">
              {product.offer_id} · {product.category} · {product.source}
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-stats">
          <div className="mstat">
            <span className="label">Цена</span>
            <span className="value">
              {Number(product.price).toLocaleString('ru-RU')} ₽
              {hasOld && (
                <s className="dim">
                  {Number(product.old_price).toLocaleString('ru-RU')} ₽
                </s>
              )}
            </span>
          </div>
          <div className="mstat">
            <span className="label">Остаток</span>
            <span className="value">{product.stock} шт</span>
          </div>
          <div className="mstat">
            <span className="label">Мин / Макс</span>
            <span className="value">
              {min.toLocaleString('ru-RU')} / {max.toLocaleString('ru-RU')} ₽
            </span>
          </div>
        </div>

        <div className="chart-box">
          {loading ? (
            <div className="empty">Загрузка графика…</div>
          ) : error ? (
            <div className="empty" style={{ color: 'var(--danger)' }}>{error}</div>
          ) : history.length === 0 ? (
            <div className="empty">История цен пока пуста</div>
          ) : (
            <Line data={chartData} options={options} />
          )}
        </div>

        <div className="modal-actions">
          <a
            className="btn"
            href={exportHistoryUrl(product.id)}
            download
          >
            Скачать историю (CSV)
          </a>
        </div>
      </div>
    </div>
  )
}
