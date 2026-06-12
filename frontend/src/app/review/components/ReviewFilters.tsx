'use client'

import { useState } from "react"

interface Props {
  onApply: (filters: Record<string, string>) => void
}

export default function ReviewFilters({ onApply }: Props) {

  const [sentiment, setSentiment] = useState('')
  const [status, setStatus] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const handleApply = () => {
    const filters: Record<string, string> = {}
    if (sentiment) filters.sentiment = sentiment
    if (status) filters.status = status
    if (dateFrom) filters.date_from = dateFrom
    if (dateTo) filters.date_to = dateTo

    onApply(filters)
  }

  return (
    <div className="grid gap-3 border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 md:grid-cols-[repeat(4,minmax(0,1fr))_auto]">
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Sentiment</label>
        <select value={sentiment} onChange={e => setSentiment(e.target.value)} className="mt-1 min-h-10 w-full border border-slate-300 bg-slate-50 px-3 text-sm text-slate-900 outline-none focus:border-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-slate-300">
          <option value="">All</option>
          <option value="POSITIVE">Positive</option>
          <option value="NEUTRAL">Neutral</option>
          <option value="NEGATIVE">Negative</option>
        </select>
      </div>

      <div>
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Status</label>
        <select value={status} onChange={e => setStatus(e.target.value)} className="mt-1 min-h-10 w-full border border-slate-300 bg-slate-50 px-3 text-sm text-slate-900 outline-none focus:border-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-slate-300">
          <option value="">All</option>
          <option value="Accepted">Accepted</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      <div>
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">From</label>
        <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="mt-1 min-h-10 w-full border border-slate-300 bg-slate-50 px-3 text-sm text-slate-900 outline-none focus:border-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-slate-300" />
      </div>

      <div>
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">To</label>
        <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} className="mt-1 min-h-10 w-full border border-slate-300 bg-slate-50 px-3 text-sm text-slate-900 outline-none focus:border-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-slate-300" />
      </div>

      <button onClick={handleApply} className="min-h-10 self-end bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200">
        Apply Filters
      </button>
    </div>
  )
}
