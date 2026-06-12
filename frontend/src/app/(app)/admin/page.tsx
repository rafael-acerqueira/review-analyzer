'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { deleteReview, listReview } from '../../lib/reviewService'
import ReviewFilters from '../../review/components/ReviewFilters'
import ReviewDetailsModal from '../../review/components/ReviewDetailsModal'
import toast, { Toaster } from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'

export default function AdminPage() {

  const [selectedReview, setSelectedReview] = useState(null)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const queryClient = useQueryClient()
  const router = useRouter()

  const { data: reviews = [], isLoading, error } = useQuery({
    queryKey: ['reviews', filters],
    queryFn: () => listReview(filters),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteReview(id),
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
      <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mx-auto max-w-7xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
        >
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Loading reviews...</span>
        </motion.div>
      </div>
    )
  }
  if (error) return null

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <Toaster position="top-right" />

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="mx-auto flex max-w-7xl flex-col gap-6"
      >
        <header className="border-b border-slate-200 pb-5 dark:border-slate-800">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Admin
          </p>
          <h1 className="mt-1 text-3xl font-semibold text-slate-950 dark:text-white">
            Reviews
          </h1>
        </header>

        <ReviewFilters onApply={setFilters} />

        <div className="overflow-x-auto border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <table className="min-w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3">Sentiment</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3 text-right">Actions</th>
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
                    className="border-b border-slate-100 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-950"
                  >
                    <td className="px-4 py-3">
                      <span className={`border px-2.5 py-1 font-semibold text-xs
                        ${r.sentiment === 'positive' || r.sentiment === 'POSITIVE' ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200'
                          : r.sentiment === 'negative' || r.sentiment === 'NEGATIVE' ? 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200'
                            : 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200'}`}>
                        {r.sentiment}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`border px-2.5 py-1 font-bold uppercase text-xs
                        ${r.status === 'Accepted' ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200'
                          : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200'}`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                      {format(new Date(r.created_at), 'yyyy-MM-dd HH:mm')}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => setSelectedReview(r)}
                          className="min-h-9 border border-slate-300 bg-white px-3 py-1 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
                        >
                          View
                        </button>
                        <button
                          onClick={() => handleDelete(r.id)}
                          className="min-h-9 border border-rose-200 bg-rose-50 px-3 py-1 text-sm font-semibold text-rose-700 transition hover:bg-rose-100 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200 dark:hover:bg-rose-900"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                )))
                  : (
                    <tr>
                      <td colSpan={4} className='py-8 text-center text-sm text-slate-500 dark:text-slate-400'>No records found.</td>
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
