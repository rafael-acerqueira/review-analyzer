'use client'

import { getStats } from '@/app/lib/reviewService'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { SentimentPie } from '../components/SentimentPie'
import { StatusBar } from '../components/StatusBar'
import { motion } from 'framer-motion'
import { Toaster } from 'react-hot-toast'

export default function AdminDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => getStats(),
  })

  if (isLoading) return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto max-w-7xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Loading dashboard...</span>
      </motion.div>
    </div>
  )
  if (error) return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto max-w-7xl border border-rose-200 bg-rose-50 p-6 dark:border-rose-900 dark:bg-rose-950"
      >
        <span className="text-sm font-semibold text-rose-700 dark:text-rose-200">Failed to load stats.</span>
      </motion.div>
    </div>
  )
  if (!data) return null

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-50 px-4 py-6 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <Toaster position="top-right" />
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="mx-auto flex max-w-7xl flex-col gap-6"
      >
        <header className="flex flex-col gap-3 border-b border-slate-200 pb-5 dark:border-slate-800 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Admin
            </p>
            <h1 className="mt-1 text-3xl font-semibold text-slate-950 dark:text-white">Dashboard</h1>
          </div>
          <Link href="/admin" className="inline-flex min-h-10 items-center border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800">Reviews</Link>
        </header>

        <div className="grid gap-4 sm:grid-cols-3">
          <motion.div whileHover={{ y: -2 }} className="border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Total Reviews</span>
            <span className="mt-2 block text-3xl font-semibold text-slate-950 dark:text-white">{data.total_reviews}</span>
          </motion.div>
          <motion.div whileHover={{ y: -2 }} className="border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-900 dark:bg-emerald-950">
            <span className="text-xs font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">Accepted</span>
            <span className="mt-2 block text-3xl font-semibold text-emerald-800 dark:text-emerald-200">{data.percent_accepted?.toFixed(1) || 0}%</span>
          </motion.div>
          <motion.div whileHover={{ y: -2 }} className="border border-rose-200 bg-rose-50 p-5 dark:border-rose-900 dark:bg-rose-950">
            <span className="text-xs font-semibold uppercase tracking-wide text-rose-700 dark:text-rose-300">Rejected</span>
            <span className="mt-2 block text-3xl font-semibold text-rose-800 dark:text-rose-200">{data.percent_rejected?.toFixed(1) || 0}%</span>
          </motion.div>
        </div>

        {data.top_rejection_reasons && data.top_rejection_reasons.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"
          >
            <h2 className="border-b border-slate-200 px-5 py-4 text-base font-semibold text-slate-950 dark:border-slate-800 dark:text-white">Top Rejection Reasons</h2>
            <ul className="divide-y divide-slate-100 dark:divide-slate-800">
              {data.top_rejection_reasons.map((item: any, idx: number) => (
                <li key={idx} className="flex items-center justify-between gap-4 px-5 py-3">
                  <span className="text-sm text-slate-700 dark:text-slate-200">{item.reason}</span>
                  <span className="font-mono text-sm font-semibold text-slate-950 dark:text-white">{item.count}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid gap-4 xl:grid-cols-2"
        >
          <SentimentPie by_sentiment={data.by_sentiment} />
          <StatusBar by_status={data.by_status} />
        </motion.div>
      </motion.div>
    </div>
  )
}
