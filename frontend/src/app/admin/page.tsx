
'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { useState } from 'react'
import { deleteReview, listReview } from '../lib/reviewService'
import ReviewFilters from '../review/components/ReviewFilters'


export default function AdminPage() {
  const [filters, setFilters] = useState<Record<string, string>>({})
  const queryClient = useQueryClient()


  const { data: reviews = [], isLoading, error } = useQuery({
    queryKey: ['reviews', filters],
    queryFn: () => listReview(filters),
  })


  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteReview(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    }
  })


  const handleDelete = async (id: number) => {
    const confirm = window.confirm('Are you sure you want to delete this review?')
    if (!confirm) return

    deleteMutation.mutate(id)
  }

  if (isLoading) return <p className="text-center mt-8">Loading...</p>
  if (error) return <p className="text-red-500 text-center mt-8">{error.message}</p>

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-semibold mb-6 text-center">Admin Panel - Reviews</h1>
      <div className="overflow-x-auto border rounded-xl shadow-sm">
        <ReviewFilters onApply={setFilters} />
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-gray-600">
            <tr>
              <th className="px-4 py-2 text-left">Original Text</th>
              <th className="px-4 py-2">Sentiment</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Feedback</th>
              <th className="px-4 py-2">Suggestion</th>
              <th className="px-4 py-2">Corrected Text</th>
              <th className="px-4 py-2">Created</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {reviews.length > 0 ? (reviews.map((r: any) => (
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-2 max-w-xs truncate" title={r.text}>{r.text}</td>
                <td className="px-4 py-2 text-center">{r.sentiment}</td>
                <td className="px-4 py-2 text-center">{r.status}</td>
                <td className="px-4 py-2 max-w-xs truncate" title={r.feedback}>{r.feedback}</td>
                <td className="px-4 py-2 max-w-xs truncate" title={r.suggestion}>{r.suggestion}</td>
                <td className="px-4 py-2 max-w-xs truncate" title={r.corrected_text}>{r.corrected_text}</td>
                <td className="px-4 py-2 text-center">{format(new Date(r.created_at), 'yyyy-MM-dd HH:mm')}</td>
                <td className="px-4 py-2 text-center">
                  <button
                    onClick={() => handleDelete(r.id)}
                    className="text-sm bg-red-900 hover:bg-red-800 text-white px-3 py-1 rounded"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            )))
              : (
                <tr className="border-t hover:bg-gray-50">
                  <td colSpan={7} className='text-center'>No records found!</td>
                </tr>)}
          </tbody>
        </table>
      </div>
    </div>
  )
}