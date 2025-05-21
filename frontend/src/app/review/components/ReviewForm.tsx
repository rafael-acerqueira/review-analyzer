'use client'

import { useState } from "react"
import { useMutation } from '@tanstack/react-query'
import { submitReviewRequest } from '../../lib/reviewService'
import toast, { Toaster } from "react-hot-toast"
import { motion, AnimatePresence } from 'framer-motion'

export default function ReviewForm() {
  const [review, setReview] = useState('')
  const [approved, setApproved] = useState(false)
  const [llmFeedback, setLlmFeedback] = useState<any | null>(null)

  const mutation = useMutation({
    mutationFn: () => submitReviewRequest({ text: review }),
    onSuccess: (data) => {
      setLlmFeedback(data)
      if (data.status === 'Accepted') {
        setApproved(true)
        toast.success('✅ Review accepted! Confirm submission below.')
      } else {
        setApproved(false)
        toast.error('❌ Review rejected. See the feedback.')
      }
    },
    onError: (error: any) => {
      toast.error(error.message || 'Unexpected Error.')
    },
  })

  const confirmSubmission = () => {
    toast.success('Review confirmed and saved!')
    setReview('')
    setApproved(false)
    setLlmFeedback(null)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  const discardReview = () => {
    setReview('')
    setApproved(false)
    setLlmFeedback(null)
    toast('Review discarded. You can write a new one.', { icon: '🗑️' })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-lg w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6 space-y-5">
        <Toaster position="top-right" />

        <h1 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-100">AI Review Analyzer</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            className="w-full border border-gray-300 rounded-xl mb-0 p-4 bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100 resize-none h-40 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Tell me your thoughts"
            required
            value={review}
            onChange={(e) => setReview(e.target.value)}
            disabled={mutation.isPending}
            readOnly={approved}
          />

          {approved && (
            <p className="text-xs text-gray-500">Review approved. You can't edit it. Confirm or discard.</p>
          )}

          {!approved && (
            <button
              type="submit"
              className="w-full bg-blue-900 hover:bg-blue-800 text-white font-semibold py-3 rounded-xl transition disabled:opacity-50 cursor-pointer"
              disabled={mutation.isPending}
              data-testid="send-to-analysis"
            >
              {mutation.isPending ? 'Analyzing...' : 'Send for Analysis'}
            </button>
          )}

          <AnimatePresence>
            {approved && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="flex gap-4"
              >
                <button
                  type="button"
                  data-testid="confirm-and-submit"
                  onClick={confirmSubmission}
                  className="flex-1 bg-green-900 hover:bg-green-800 text-white py-3 font-semibold rounded-xl transition cursor-pointer"
                >
                  Confirm and Submit
                </button>

                <button
                  type="button"
                  onClick={discardReview}
                  data-testid="discard"
                  className="flex-1 bg-red-900 hover:bg-red-800 text-white py-3 font-semibold rounded-xl transition cursor-pointer"
                >
                  Discard
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence>
            {llmFeedback && (
              <motion.div
                key="feedback"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="p-4 bg-gray-100 dark:bg-gray-700 border dark:border-gray-600 rounded-xl space-y-4 text-base text-gray-800 dark:text-gray-100"
              >
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${llmFeedback.sentiment === 'POSITIVE'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                    }`}>
                    {llmFeedback.sentiment}
                  </span>
                  <span className="text-xs text-gray-500">
                    Confidence: {(llmFeedback.polarity * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase ${llmFeedback.status === 'Accepted'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                    }`}>
                    {llmFeedback.status === 'Accepted' ? 'ACCEPT' : 'REJECT'}
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-300 italic" data-testid="feedback-message">
                    {llmFeedback.feedback}
                  </span>
                </div>

                {llmFeedback.suggestion && llmFeedback.suggestion.trim() !== '' && (
                  <div className="p-3 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-100 rounded-md italic" data-testid="sugestion-text">
                    <strong>Suggestion:</strong> {llmFeedback.suggestion}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </form>
      </div >
    </div >
  )
}