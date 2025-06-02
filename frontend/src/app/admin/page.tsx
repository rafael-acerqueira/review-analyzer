
'use client'



import { useMutation } from '@tanstack/react-query'
import { format } from 'date-fns'
import { useEffect, useState } from 'react'
import { deleteReview, listReview } from '../lib/reviewService'

interface Review {
  id: number
  sentiment: string
  polarity: number
  status: 'Accepted' | 'Rejected'
  feedback: string
  suggestion?: string
}


export default function AdminPage() {
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')


  const mutation = useMutation({
    mutationFn: () => listReview(),
    onSuccess: (data) => {
      setReviews(data)
      setLoading(false)
    },
    onError: (error: unknown) => {
      if (error instanceof Error) {
        setError(error.message)
        setLoading(false)
      }
    },
  })


  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteReview(id),
    onSuccess: (data) => {
      setReviews(reviews => reviews.filter(r => r.id != data["review_id"]))
    },
    onError: (error: unknown) => {
      if (error instanceof Error) {
        setError(error.message)
      }
    },
  })

  useEffect(() => {
    mutation.mutate()
  }, [])


  const handleDelete = async (id: number) => {
    const confirm = window.confirm('Are you sure you want to delete this review?')
    if (!confirm) return

    deleteMutation.mutate(id)
  }

  if (loading) return <p className="text-center mt-8">Loading...</p>
  if (error) return <p className="text-red-500 text-center mt-8">{error}</p>

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-semibold mb-6 text-center">Admin Panel - Reviews</h1>
      <div className="overflow-x-auto border rounded-xl shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-gray-600">
            <tr>
              <th className="px-4 py-2 text-left">Text</th>
              <th className="px-4 py-2">Sentiment</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Feedback</th>
              <th className="px-4 py-2">Created</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {reviews.map((r: any) => (
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-2 max-w-xs truncate" title={r.text}>{r.text}</td>
                <td className="px-4 py-2 text-center">{r.sentiment}</td>
                <td className="px-4 py-2 text-center">{r.status}</td>
                <td className="px-4 py-2 max-w-xs truncate" title={r.feedback}>{r.feedback}</td>
                <td className="px-4 py-2 text-center">{format(new Date(r.created_at), 'yyyy-MM-dd HH:mm')}</td>
                <td className="px-4 py-2 text-center">
                  <button
                    onClick={() => handleDelete(r.id)}
                    className="text-sm bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}