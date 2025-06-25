'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { deleteReview, listReview } from '../../lib/reviewService'
import ReviewFilters from '../../review/components/ReviewFilters'
import ReviewDetailsModal from '../../review/components/ReviewDetailsModal'
import toast, { Toaster } from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'

export default function AdminPage() {
  const { data: session } = useSession()
  const token = session?.user?.access_token || ""
  const [selectedReview, setSelectedReview] = useState(null)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const queryClient = useQueryClient()
  const router = useRouter()

  const { data: reviews = [], isLoading, error } = useQuery({
    queryKey: ['reviews', filters],
    queryFn: () => listReview(filters, token),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteReview(id, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
      toast.success('Review deleted.')
    }
  })

  const handleDelete = async (id: number) => {
    const confirm = window.confirm('Are you sure you want to delete this review?')
    if (!confirm) return
    deleteMutation.mutate(id)
  }

  useEffect(() => {
    if (error) {
      toast.error(error.message || 'Unexpected Error.')
      router.push('/')
    }
  }, [error, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-8 flex flex-col items-center"
        >
          <span className="text-xl text-blue-900 dark:text-blue-200 font-semibold mb-2">Loading reviews...</span>
        </motion.div>
      </div>
    )
  }
  if (error) return null

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <Toaster position="top-right" />

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="max-w-5xl w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-8 space-y-8"
      >
        <h1 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-100 mb-6">
          Admin Panel - Reviews
        </h1>
        <ReviewFilters onApply={setFilters} />

        <div className="overflow-x-auto border rounded-xl shadow-sm bg-gray-100 dark:bg-gray-700 p-2">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
              <tr>
                <th className="px-4 py-2">Sentiment</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Created</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              <AnimatePresence>
                {reviews.length > 0 ? (reviews.map((r: any) => (
                  <motion.tr
                    key={r.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="border-t dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <td className="px-4 py-2 text-center">
                      <span className={`px-2 py-1 rounded-full font-semibold text-xs
                        ${r.sentiment === 'positive' ? 'bg-green-100 text-green-700'
                          : r.sentiment === 'negative' ? 'bg-red-100 text-red-700'
                            : 'bg-gray-200 text-gray-700'}`}>
                        {r.sentiment}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-center">
                      <span className={`px-2 py-1 rounded-full font-bold uppercase text-xs
                        ${r.status === 'Accepted' ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'}`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-center">
                      {format(new Date(r.created_at), 'yyyy-MM-dd HH:mm')}
                    </td>
                    <td className="px-4 py-2 text-center">
                      <div className="flex justify-center gap-2">
                        <button
                          onClick={() => setSelectedReview(r)}
                          className="text-sm bg-blue-900 hover:bg-blue-800 text-white px-3 py-1 rounded transition"
                        >
                          View
                        </button>
                        <button
                          onClick={() => handleDelete(r.id)}
                          className="text-sm bg-red-900 hover:bg-red-800 text-white px-3 py-1 rounded transition"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                )))
                  : (
                    <tr className="border-t dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td colSpan={4} className='text-center text-gray-500 dark:text-gray-300 py-4'>No records found!</td>
                    </tr>)}
              </AnimatePresence>
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
      </motion.div>
    </div>
  )
}
