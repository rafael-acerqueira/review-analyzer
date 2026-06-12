'use client'

import { useState } from "react"
import { useMutation } from '@tanstack/react-query'
import { submitReviewRequest, createReview } from '../../lib/reviewService'
import toast, { Toaster } from "react-hot-toast"
import { motion, AnimatePresence } from 'framer-motion'
import { FaCheck, FaPaperPlane, FaRegLightbulb, FaTrash } from 'react-icons/fa'

interface LLMFeedback {
  sentiment: string
  polarity: number
  status: 'Accepted' | 'Rejected'
  feedback: string
  suggestion?: string
}

export default function ReviewForm() {
  const [review, setReview] = useState('')
  const [originalReview, setOriginalReview] = useState('')
  const [correctedText, setCorrectedText] = useState('')
  const [fillCorrectedText, setFillCorrectedText] = useState(false)
  const [approved, setApproved] = useState(false)
  const [llmFeedback, setLlmFeedback] = useState<LLMFeedback | null>(null)

  const mutation = useMutation({
    mutationFn: () => submitReviewRequest({ text: review }),
    onSuccess: (data) => {
      setLlmFeedback(data)
      if (originalReview == '') {
        setOriginalReview(review)
      }


      if (data.status === 'Accepted') {
        setApproved(true)

        if (fillCorrectedText) {
          setCorrectedText(review)
        }

        toast.success('✅ Review accepted! Confirm submission below.')
      } else {
        setApproved(false)
        setFillCorrectedText(true)

        toast.error('❌ Review rejected. See the feedback.')
      }
    },
    onError: (error: unknown) => {
      if (error instanceof Error) {
        toast.error(error.message || 'Unexpected Error.')
      }
    },
  })

  const createMutation = useMutation({
    mutationFn: async () => {

      if (!llmFeedback) {
        throw new Error('LLM is missing.');
      }
      return createReview({
        text: originalReview,
        corrected_text: correctedText,
        sentiment: llmFeedback.sentiment,
        status: llmFeedback.status,
        feedback: llmFeedback.feedback,
        suggestion: llmFeedback.suggestion,
      })
    },
    onSuccess: () => {
      toast.success('Review confirmed and saved!')
      setReview('')
      setOriginalReview('')
      setCorrectedText('')
      setApproved(false)
      setLlmFeedback(null)

    },
    onError: (error: unknown) => {
      if (error instanceof Error) {
        toast.error(error.message || 'Unexpected Error.')
      }
    },
  })

  const confirmSubmission = async (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  const discardReview = () => {
    setReview('')
    setCorrectedText('')
    setApproved(false)
    setLlmFeedback(null)
    toast('Review discarded. You can write a new one.', { icon: '🗑️' })
  }

  const wordCount = review.trim() ? review.trim().split(/\s+/).length : 0
  const isAccepted = llmFeedback?.status === 'Accepted'

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <Toaster position="top-right" />

      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-3 border-b border-slate-200 pb-5 dark:border-slate-800 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Review workspace
            </p>
            <h1 data-testid="title" className="mt-1 text-3xl font-semibold text-slate-950 dark:text-white">
              AI Review Analyzer
            </h1>
          </div>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div className="border border-slate-200 bg-white px-3 py-2 dark:border-slate-800 dark:bg-slate-900">
              <div className="text-slate-500 dark:text-slate-400">Words</div>
              <div className="font-semibold">{wordCount}</div>
            </div>
            <div className="border border-slate-200 bg-white px-3 py-2 dark:border-slate-800 dark:bg-slate-900">
              <div className="text-slate-500 dark:text-slate-400">Status</div>
              <div className="font-semibold">{llmFeedback?.status || 'Draft'}</div>
            </div>
            <div className="border border-slate-200 bg-white px-3 py-2 dark:border-slate-800 dark:bg-slate-900">
              <div className="text-slate-500 dark:text-slate-400">Sentiment</div>
              <div className="font-semibold">{llmFeedback?.sentiment || 'Pending'}</div>
            </div>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
          <section className="border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
              <div>
                <h2 className="text-base font-semibold">Review draft</h2>
              </div>
              {approved && (
                <span className="bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                  Locked
                </span>
              )}
            </div>

            <div className="p-5">
              <textarea
                className="min-h-[340px] w-full resize-none border border-slate-300 bg-slate-50 p-4 text-base leading-7 text-slate-950 outline-none transition focus:border-slate-900 disabled:opacity-70 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-slate-300"
                placeholder="Tell me your thoughts"
                required
                value={review}
                onChange={(e) => setReview(e.target.value)}
                disabled={mutation.isPending}
                readOnly={approved}
              />

              {approved && (
                <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                  Review approved. Confirm submission or discard this draft.
                </p>
              )}

              <div className="mt-5 flex flex-col gap-3 sm:flex-row">
                {!approved && (
                  <button
                    type="submit"
                    className="inline-flex min-h-11 items-center justify-center gap-2 bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
                    disabled={mutation.isPending}
                    data-testid="send-to-analysis"
                  >
                    <FaPaperPlane aria-hidden="true" />
                    {mutation.isPending ? 'Analyzing...' : 'Send for Analysis'}
                  </button>
                )}

                <AnimatePresence>
                  {approved && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="flex w-full flex-col gap-3 sm:flex-row"
                    >
                      <button
                        type="button"
                        data-testid="confirm-and-submit"
                        onClick={confirmSubmission}
                        disabled={createMutation.isPending}
                        className="inline-flex min-h-11 flex-1 items-center justify-center gap-2 bg-emerald-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <FaCheck aria-hidden="true" />
                        {createMutation.isPending ? 'Saving...' : 'Confirm and Submit'}
                      </button>

                      <button
                        type="button"
                        onClick={discardReview}
                        data-testid="discard"
                        className="inline-flex min-h-11 flex-1 items-center justify-center gap-2 border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:hover:bg-slate-900"
                      >
                        <FaTrash aria-hidden="true" />
                        Discard
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </section>

          <aside className="border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
            <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
              <h2 className="text-base font-semibold">Analysis</h2>
            </div>

            <div className="p-5">
              <AnimatePresence mode="wait">
                {llmFeedback ? (
                  <motion.div
                    key="feedback"
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.25 }}
                    className="space-y-5"
                  >
                    <div className="grid grid-cols-2 gap-3">
                      <div className="border border-slate-200 p-3 dark:border-slate-800">
                        <div className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">Sentiment</div>
                        <div className={`mt-2 text-sm font-semibold ${llmFeedback.sentiment === 'POSITIVE'
                          ? 'text-emerald-700 dark:text-emerald-300'
                          : 'text-rose-700 dark:text-rose-300'
                          }`}>
                          {llmFeedback.sentiment}
                        </div>
                      </div>
                      <div className="border border-slate-200 p-3 dark:border-slate-800">
                        <div className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">Confidence</div>
                        <div className="mt-2 text-sm font-semibold">
                          {(llmFeedback.polarity * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    <div className={`border-l-4 p-4 ${isAccepted
                      ? 'border-emerald-600 bg-emerald-50 text-emerald-950 dark:bg-emerald-950 dark:text-emerald-100'
                      : 'border-rose-600 bg-rose-50 text-rose-950 dark:bg-rose-950 dark:text-rose-100'
                      }`}>
                      <div className="mb-2 text-xs font-bold uppercase tracking-wide">
                        {isAccepted ? 'ACCEPT' : 'REJECT'}
                      </div>
                      <p className="text-sm leading-6" data-testid="feedback-message">
                        {llmFeedback.feedback}
                      </p>
                    </div>

                    {llmFeedback.suggestion && llmFeedback.suggestion.trim() !== '' && (
                      <div className="border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950" data-testid="suggestion-text">
                        <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
                          <FaRegLightbulb aria-hidden="true" />
                          Suggestion
                        </div>
                        <p className="text-sm leading-6 text-slate-700 dark:text-slate-300">
                          {llmFeedback.suggestion}
                        </p>
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex min-h-[340px] items-center justify-center border border-dashed border-slate-300 p-6 text-center dark:border-slate-700"
                  >
                    <div>
                      <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300">
                        <FaRegLightbulb aria-hidden="true" />
                      </div>
                      <p className="text-sm font-medium">No analysis yet</p>
                      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        Awaiting review analysis.
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </aside>
        </form>
      </div>
    </div>
  )
}
