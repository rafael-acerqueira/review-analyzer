'use client'

import { useState } from "react"
import { useMutation } from '@tanstack/react-query';
import { submitReviewRequest } from '../../lib/reviewService'
import toast, { Toaster } from "react-hot-toast";

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
        toast.success('✅ Review accepted! Confirm submission below.');
      } else {
        setApproved(false);
        toast.error('❌ Review rejected. See the feedback.');
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
    <div className="max-w-lg mx-auto p-4 bg-white shadow rounded-xl space-y-4">
      <Toaster />
      <h1 className="text-xl font-bold">Client Review</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          className="w-full border rounded p-2"
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
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? 'Analyzing...' : 'Send for Analysis'}
          </button>
        )}

        {approved && (
          <button
            type="button"
            onClick={confirmSubmission}
            className="bg-green-600 text-white px-4 py-2 rounded"
          >
            Confirm and Submit Assessment
          </button>
        )}

        {llmFeedback && (
          <div className="mt-4 p-4 border rounded bg-gray-100 space-y-2">
            <p><strong>Status:</strong> {llmFeedback.status}</p>
            <p><strong>Sentiment:</strong> {llmFeedback.sentiment}</p>
            <p><strong>Feedback da IA:</strong> {llmFeedback.feedback}</p>
          </div>
        )}

      </form>
    </div>
  )
}