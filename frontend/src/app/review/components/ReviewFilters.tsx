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
    <div className="flex flex-wrap gap-4 mb-6 bg-gray-50 p-4 rounded-xl shadow-sm">
      <div>
        <label className="block text-sm font-medium">Sentiment</label>
        <select value={sentiment} onChange={e => setSentiment(e.target.value)} className="mt-1 p-2 border rounded text-sm">
          <option value="">All</option>
          <option value="POSITIVE">Positive</option>
          <option value="NEUTRAL">Neutral</option>
          <option value="NEGATIVE">Negative</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium">Status</label>
        <select value={status} onChange={e => setStatus(e.target.value)} className="mt-1 p-2 border rounded text-sm">
          <option value="">All</option>
          <option value="Accepted">Accepted</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium">From</label>
        <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="mt-1 p-2 border rounded text-sm" />
      </div>

      <div>
        <label className="block text-sm font-medium">To</label>
        <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} className="mt-1 p-2 border rounded text-sm" />
      </div>

      <button onClick={handleApply} className="self-end  bg-blue-900 hover:bg-blue-800 text-white px-4 py-2 rounded text-sm">
        Apply Filters
      </button>
    </div>
  )
}