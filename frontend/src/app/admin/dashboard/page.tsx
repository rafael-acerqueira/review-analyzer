'use client'

import { getStats } from '@/app/lib/reviewService'
import { useQuery } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
import Link from 'next/link'
import { SentimentPie } from '../components/SentimentPie'
import { StatusBar } from '../components/StatusBar'
import { motion } from 'framer-motion'
import { Toaster } from 'react-hot-toast'

export default function AdminDashboard() {
  const { data: session } = useSession()
  const token = session?.user?.access_token || ""
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => getStats(token),
  })

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-8 flex flex-col items-center"
      >
        <span className="text-xl text-blue-900 dark:text-blue-200 font-semibold mb-2">Loading dashboard...</span>
      </motion.div>
    </div>
  )
  if (error) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-8 flex flex-col items-center"
      >
        <span className="text-xl text-red-700 dark:text-red-400 font-semibold mb-2">Failed to load stats.</span>
      </motion.div>
    </div>
  )
  if (!data) return null

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <Toaster position="top-right" />
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="max-w-4xl w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-8 space-y-8 my-8"
      >
        <div className="flex flex-col sm:flex-row justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 sm:mb-0">Admin Dashboard</h1>
          <Link href="/admin" className="text-blue-700 dark:text-blue-400 hover:underline font-semibold">← Reviews</Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
          <motion.div whileHover={{ scale: 1.03 }} className="bg-gray-100 dark:bg-gray-700 rounded-xl shadow p-6 flex flex-col items-center">
            <span className="text-lg font-semibold text-gray-700 dark:text-gray-200">Total Reviews</span>
            <span className="text-3xl font-bold text-blue-900 dark:text-blue-300">{data.total_reviews}</span>
          </motion.div>
          <motion.div whileHover={{ scale: 1.03 }} className="bg-green-50 dark:bg-green-900 rounded-xl shadow p-6 flex flex-col items-center">
            <span className="text-lg font-semibold text-gray-700 dark:text-gray-200">Accepted (%)</span>
            <span className="text-3xl font-bold text-green-800 dark:text-green-400">{data.percent_accepted?.toFixed(1) || 0}%</span>
          </motion.div>
          <motion.div whileHover={{ scale: 1.03 }} className="bg-red-50 dark:bg-red-900 rounded-xl shadow p-6 flex flex-col items-center">
            <span className="text-lg font-semibold text-gray-700 dark:text-gray-200">Rejected (%)</span>
            <span className="text-3xl font-bold text-red-800 dark:text-red-400">{data.percent_rejected?.toFixed(1) || 0}%</span>
          </motion.div>
        </div>

        {data.top_rejection_reasons && data.top_rejection_reasons.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-3">Top Rejection Reasons</h2>
            <ul className="bg-gray-100 dark:bg-gray-700 rounded-xl shadow p-4 space-y-2">
              {data.top_rejection_reasons.map((item: any, idx: number) => (
                <li key={idx} className="flex justify-between items-center">
                  <span className="text-gray-700 dark:text-gray-200">{item.reason}</span>
                  <span className="font-mono text-blue-900 dark:text-blue-300">{item.count}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-100 dark:bg-gray-700 rounded-2xl shadow p-8 flex flex-col items-center"
        >
          <SentimentPie by_sentiment={data.by_sentiment} />
          <StatusBar by_status={data.by_status} />
        </motion.div>
      </motion.div>
    </div>
  )
}
