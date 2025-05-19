'use client'

import { useState } from "react"
import { useMutation } from '@tanstack/react-query';
import { submitReviewRequest } from '../../lib/reviewService'
import toast, { Toaster } from "react-hot-toast";
import { motion, AnimatePresence } from 'framer-motion';

export default function ReviewForm() {
  const [review, setReview] = useState('')
  const [approved, setApproved] = useState(false)
  const [llmFeedback, setLlmFeedback] = useState<any | null>(null);

  const mutation = useMutation({
    mutationFn: () => submitReviewRequest({ text: review }),
    onSuccess: (data) => {
      setLlmFeedback(data);
      if (data.status === 'Accepted') {
        setApproved(true);
        toast.success('Review accepted! Confirm submission below.');
      } else {
        setApproved(false);
        toast.error('Review rejected. See the feedback.');
      }
    },
    onError: (error: any) => {
      toast.error(error.message || 'Unexpected Error.');

    },
  })


  const confirmSubmission = () => {
    toast.success('Review confirmed and saved!');
    // call db to save this record
    setReview('');
    setApproved(false);
    setLlmFeedback(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="max-w-lg w-full bg-white shadow-xl rounded-2xl p-6 space-y-5">
        <Toaster position="top-right" />
        <h1 className="text-2xl font-bold text-center text-gray-800">Client Review</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            className="w-full border border-gray-300 rounded-xl p-4 text-gray-800 resize-none h-40 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Tell me your thoughts"
            rows={5}
            required
            value={review}
            onChange={(e) => setReview(e.target.value)}
            disabled={mutation.isPending}
          />
          {!approved && (
            <button
              type="submit"
              className="w-full bg-blue-600 text-white font-semibold py-3 rounded-xl hover:bg-blue-700 transition disabled:opacity-50"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? 'Analyzing...' : 'Send for Analysis'}
            </button>
          )}

          <AnimatePresence>
            {approved && (
              <motion.button
                type="button"
                key="confirm"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                onClick={confirmSubmission}
                className="w-full bg-green-600 text-white py-3 font-semibold rounded-xl hover:bg-green-700 transition"
              >
                Confirm and Submit Assessment
              </motion.button>
            )}
          </AnimatePresence>

          <AnimatePresence>
            {llmFeedback && (
              <motion.div key="feedback"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="p-4 bg-gray-50 border rounded-xl space-y-2 text-sm text-gray-700"
              >
                <p><strong>Status:</strong> <span className="text-gray-900">{llmFeedback.status}</span></p>
                <p><strong>Sentiment:</strong> <span className="text-gray-900">{llmFeedback.sentiment}</span></p>
                <p><strong>AI Feedback:</strong> <span className="italic">{llmFeedback.feedback}</span></p>
              </motion.div>
            )}
          </AnimatePresence>



        </form>
      </div>
    </div >
  )
}