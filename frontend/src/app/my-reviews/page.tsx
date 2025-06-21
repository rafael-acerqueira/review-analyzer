'use client'

import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { getMyReviews } from '../lib/reviewService'
import Link from 'next/link'
import LogoutButton from '../review/components/LogoutButton'
import { motion, AnimatePresence } from 'framer-motion'

export default function MyReviewsPage() {
  const { data: session } = useSession()
  const token = session?.user?.access_token || ""

  const { data: reviews = [], isLoading, error } = useQuery({
    queryKey: ['my-reviews'],
    queryFn: () => getMyReviews(token),
    enabled: !!token
  })

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6 space-y-5 text-center">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4">My Reviews</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-2">Login required to view your reviews.</p>
          <Link href="/" className="text-blue-700 dark:text-blue-400 hover:underline">← Back to Home</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="absolute top-4 right-4">
        <LogoutButton />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="max-w-lg w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6 space-y-5"
      >
        <h1 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-100 mb-4">
          My Reviews
        </h1>
        {isLoading && <p className="text-center text-gray-500">Loading...</p>}
        {error && <p className="text-center text-red-500">Failed to load your reviews.</p>}
        {!isLoading && reviews.length === 0 && (
          <p className="text-center text-gray-500">You haven’t submitted any reviews yet.</p>
        )}
        <ul className="space-y-3">
          <AnimatePresence>
            {reviews.map((review: any) => (
              <motion.li
                key={review.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="bg-gray-100 dark:bg-gray-700 p-4 rounded-xl shadow"
              >
                <div className="mb-4 flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="text-xs text-gray-500 mb-1">Original</div>
                    <div className="text-base text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-800 p-2 rounded-lg">
                      {review.text}
                    </div>
                  </div>
                  {review.corrected_text && review.corrected_text.trim() !== "" && (
                    <div className="flex-1">
                      <div className="text-xs text-gray-500 mb-1">Corrected</div>
                      <div className="text-base text-blue-900 dark:text-blue-200 bg-blue-50 dark:bg-blue-900 p-2 rounded-lg">
                        {review.corrected_text}
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex gap-3 text-xs justify-center">
                  <span className={`px-2 py-1 rounded-full font-semibold ${review.sentiment === 'positive' ? 'bg-green-100 text-green-700' : review.sentiment === 'negative' ? 'bg-red-100 text-red-700' : 'bg-gray-200 text-gray-700'}`}>
                    {review.sentiment}
                  </span>
                  <span className={`px-2 py-1 rounded-full font-bold uppercase ${review.status === 'Accepted' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {review.status}
                  </span>
                </div>
                {review.feedback && (
                  <div className="mt-2 text-xs italic text-gray-600 dark:text-gray-300 text-center">
                    {review.feedback}
                  </div>
                )}
                {review.suggestion && review.suggestion.trim() !== '' && (
                  <div className="mt-1 text-xs text-blue-800 dark:text-blue-200 text-center">
                    <strong>Suggestion:</strong> {review.suggestion}
                  </div>
                )}
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
        <div className="text-center mt-4">
          <Link href="/" className="text-blue-700 dark:text-blue-400 hover:underline">
            ← Back to Home
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
