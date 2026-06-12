'use client'

import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { getMyReviews } from '../../lib/reviewService'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { FaArrowLeft, FaRegFileAlt } from 'react-icons/fa'

export default function MyReviewsPage() {
  const { status } = useSession()
  const isAuthed = status === 'authenticated'

  const { data: reviews = [], isLoading, error } = useQuery({
    queryKey: ['my-reviews'],
    queryFn: () => getMyReviews(),
    enabled: isAuthed
  })

  if (!isAuthed) {
    return (
      <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
          <h1 className="text-2xl font-semibold">My Reviews</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Login required to view your reviews.</p>
          <Link href="/login" className="mt-5 inline-flex min-h-10 items-center gap-2 border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-100 dark:hover:bg-slate-800">
            <FaArrowLeft aria-hidden="true" />
            Login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="mx-auto flex max-w-7xl flex-col gap-6"
      >
        <header className="flex flex-col gap-3 border-b border-slate-200 pb-5 dark:border-slate-800 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Review history
            </p>
            <h1 className="mt-1 text-3xl font-semibold text-slate-950 dark:text-white">
              My Reviews
            </h1>
          </div>
          <Link href="/" className="inline-flex min-h-10 items-center gap-2 border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800">
            <FaArrowLeft aria-hidden="true" />
            New Review
          </Link>
        </header>

        {isLoading && (
          <div className="border border-slate-200 bg-white p-6 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
            Loading reviews...
          </div>
        )}
        {error && (
          <div className="border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
            Failed to load your reviews.
          </div>
        )}
        {!isLoading && reviews.length === 0 && (
          <div className="flex min-h-[220px] items-center justify-center border border-dashed border-slate-300 bg-white p-6 text-center dark:border-slate-700 dark:bg-slate-900">
            <div>
              <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300">
                <FaRegFileAlt aria-hidden="true" />
              </div>
              <p className="text-sm font-medium">No reviews submitted yet</p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Your confirmed analyses will appear here.</p>
            </div>
          </div>
        )}
        <ul className="grid gap-4">
          <AnimatePresence>
            {reviews.map((review: any) => (
              <motion.li
                key={review.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900"
              >
                <div className="mb-4 grid gap-4 lg:grid-cols-2">
                  <div>
                    <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Original</div>
                    <div className="min-h-24 border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-800 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200">
                      {review.text}
                    </div>
                  </div>
                  {review.corrected_text && review.corrected_text.trim() !== "" && (
                    <div>
                      <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Corrected</div>
                      <div className="min-h-24 border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-800 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200">
                        {review.corrected_text}
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className={`border px-2.5 py-1 font-semibold ${review.sentiment === 'positive' || review.sentiment === 'POSITIVE' ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200' : review.sentiment === 'negative' || review.sentiment === 'NEGATIVE' ? 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200' : 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200'}`}>
                    {review.sentiment}
                  </span>
                  <span className={`border px-2.5 py-1 font-bold uppercase ${review.status === 'Accepted' ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200' : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200'}`}>
                    {review.status}
                  </span>
                </div>
                {review.feedback && (
                  <div className="mt-4 border-l-4 border-slate-300 bg-slate-50 p-3 text-sm leading-6 text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300">
                    {review.feedback}
                  </div>
                )}
                {review.suggestion && review.suggestion.trim() !== '' && (
                  <div className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
                    <strong>Suggestion:</strong> {review.suggestion}
                  </div>
                )}
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      </motion.div>
    </div>
  )
}
