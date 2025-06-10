
'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { useState } from 'react'
import { deleteReview, listReview } from '../lib/reviewService'
import ReviewFilters from '../review/components/ReviewFilters'
import ReviewDetailsModal from '../review/components/ReviewDetailsModal'
import { useSession } from 'next-auth/react'

export default function AdminPage() {

  const { data: session } = useSession();

  const token = session?.user?.token

  const [selectedReview, setSelectedReview] = useState(null)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const queryClient = useQueryClient()


  const { data: reviews = [], isLoading, error } = useQuery({
    queryKey: ['reviews', filters],
    queryFn: () => listReview(filters, token),
  })


  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteReview(id, token),
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
              <th className="px-4 py-2">Sentiment</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Created</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {reviews.length > 0 ? (reviews.map((r: any) => (
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-2 text-center">{r.sentiment}</td>
                <td className="px-4 py-2 text-center">{r.status}</td>
                <td className="px-4 py-2 text-center">{format(new Date(r.created_at), 'yyyy-MM-dd HH:mm')}</td>
                <td className="px-4 py-2 text-center">
                  <div className="flex justify-center gap-2">
                    <button
                      onClick={() => setSelectedReview(r)}
                      className="text-sm bg-blue-900 hover:bg-blue-800 text-white px-3 py-1 rounded"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(r.id)}
                      className="text-sm bg-red-900 hover:bg-red-800 text-white px-3 py-1 rounded"
                    >
                      Delete
                    </button>
                  </div>
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
      {selectedReview && (
        <ReviewDetailsModal
          isOpen={!!selectedReview}
          onClose={() => setSelectedReview(null)}
          review={selectedReview}
        />
      )}
    </div>

  )
}