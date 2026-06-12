'use client'

import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { XMarkIcon } from '@heroicons/react/24/solid'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  review: {
    text: string
    corrected_text?: string
    feedback: string
    suggestion?: string
  }
}

export default function ReviewDetailsModal({ isOpen, onClose, review }: ModalProps) {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <div className="fixed inset-0 bg-slate-950/50" />

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-2 sm:p-4">
            <Dialog.Panel className="relative w-full max-w-2xl transform overflow-hidden border border-slate-200 bg-white text-left align-middle shadow-xl transition-all dark:border-slate-800 dark:bg-slate-900">
              <button
                onClick={onClose}
                className="absolute right-4 top-4 text-slate-500 transition hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                aria-label="Close modal"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>

              <Dialog.Title as="h3" className="border-b border-slate-200 px-5 py-4 text-base font-semibold text-slate-950 dark:border-slate-800 dark:text-white">
                Review Details
              </Dialog.Title>

              <div className="max-h-[65vh] space-y-4 overflow-y-auto p-5 text-sm text-slate-700 dark:text-slate-300">
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Original Text</p>
                  <p className="whitespace-pre-wrap border border-slate-200 bg-slate-50 p-3 leading-6 dark:border-slate-800 dark:bg-slate-950">{review.text}</p>
                </div>

                {review.corrected_text && (
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Corrected Text</p>
                    <p className="whitespace-pre-wrap border border-slate-200 bg-slate-50 p-3 leading-6 dark:border-slate-800 dark:bg-slate-950">{review.corrected_text}</p>
                  </div>
                )}

                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Feedback</p>
                  <p className="whitespace-pre-wrap border-l-4 border-slate-300 bg-slate-50 p-3 leading-6 dark:border-slate-700 dark:bg-slate-950">{review.feedback}</p>
                </div>

                {review.suggestion && (
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Suggestion</p>
                    <p className="whitespace-pre-wrap border border-slate-200 bg-slate-50 p-3 leading-6 dark:border-slate-800 dark:bg-slate-950">{review.suggestion}</p>
                  </div>
                )}
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
