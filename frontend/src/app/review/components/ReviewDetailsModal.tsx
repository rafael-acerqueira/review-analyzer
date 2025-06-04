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
        {/* Overlay */}
        <div className="fixed inset-0 bg-black/40" />

        {/* Centered modal */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-2 sm:p-4">
            {/* Modal panel */}
            <Dialog.Panel className="w-full max-w-md sm:max-w-2xl transform overflow-hidden rounded-2xl bg-white p-4 sm:p-6 text-left align-middle shadow-xl transition-all relative">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
                aria-label="Close modal"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>

              {/* Title */}
              <Dialog.Title as="h3" className="text-lg font-semibold text-gray-900 mb-4">
                Review Details
              </Dialog.Title>

              {/* Scrollable content */}
              <div className="space-y-4 text-sm text-gray-700 max-h-[60vh] overflow-y-auto pr-1">
                <div>
                  <p className="font-medium">Original Text:</p>
                  <p className="whitespace-pre-wrap">{review.text}</p>
                </div>

                {review.corrected_text && (
                  <div>
                    <p className="font-medium">Corrected Text:</p>
                    <p className="whitespace-pre-wrap">{review.corrected_text}</p>
                  </div>
                )}

                <div>
                  <p className="font-medium">Feedback:</p>
                  <p className="whitespace-pre-wrap">{review.feedback}</p>
                </div>

                {review.suggestion && (
                  <div>
                    <p className="font-medium">Suggestion:</p>
                    <p className="whitespace-pre-wrap">{review.suggestion}</p>
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