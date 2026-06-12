'use client'

import { useState } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { FcGoogle } from 'react-icons/fc'
import toast, { Toaster } from 'react-hot-toast'
import { motion } from 'framer-motion'

export default function AuthForm() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    if (mode === 'login') {
      const result = await signIn('credentials', {
        redirect: false,
        email,
        password,
      })

      if (result?.error) {
        toast.error('Invalid credentials or user not found')
      } else {
        toast.success('Welcome back!')
        router.refresh()
        router.replace('/')
      }
      setLoading(false)
    } else {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (res.ok) {
        const result = await signIn('credentials', { redirect: false, email, password })

        if (result?.error) {
          toast.error('Account created, but login failed. Please try logging in.')
          setMode('login')
          setLoading(false)
          return
        }

        toast.success('Account created!')
        router.refresh()
        router.replace('/')
        setLoading(false)
      } else {
        const data = await res.json()
        toast.error(data.detail || 'Registration failed')
        setLoading(false)
        return
      }
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8 text-slate-950 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <Toaster position="top-right" />
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-8 lg:grid-cols-[minmax(0,0.9fr)_minmax(360px,0.55fr)]"
      >
        <section className="border-b border-slate-200 pb-8 dark:border-slate-800 lg:border-b-0 lg:pb-0">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Review Analyzer
          </p>
          <h1 className="mt-2 max-w-xl text-4xl font-semibold text-slate-950 dark:text-white">
            Analyze reviews with a clearer operational workflow.
          </h1>
          <p className="mt-4 max-w-lg text-sm leading-6 text-slate-600 dark:text-slate-300">
            Sign in to submit reviews, inspect model feedback, and track review history.
          </p>
        </section>

        <section className="border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <h2 className="text-base font-semibold text-slate-950 dark:text-white">
              {mode === 'login' ? 'Login to your account' : 'Create a new account'}
            </h2>
          </div>

        <form onSubmit={handleSubmit} className="space-y-4 p-5">
          <input
            type="email"
            placeholder="Email"
            value={email}
            required
            onChange={(e) => setEmail(e.target.value)}
            className="min-h-11 w-full border border-slate-300 bg-slate-50 px-3 text-sm text-slate-950 outline-none transition focus:border-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-slate-300"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            required
            onChange={(e) => setPassword(e.target.value)}
            className="min-h-11 w-full border border-slate-300 bg-slate-50 px-3 text-sm text-slate-950 outline-none transition focus:border-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-slate-300"
          />

          <button
            type="submit"
            disabled={loading}
            className="inline-flex min-h-11 w-full items-center justify-center bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
          >
            {loading ? 'Loading...' : mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        <div className="space-y-3 border-t border-slate-200 p-5 dark:border-slate-800">
        <button
          onClick={() => signIn('google', { callbackUrl: '/' })}
          className="inline-flex min-h-11 w-full items-center justify-center gap-2 border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
        >
          <FcGoogle className="text-xl" /> Continue with Google
        </button>

        <button
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          className="inline-flex min-h-11 w-full items-center justify-center border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
        >
          {mode === 'login' ? 'Create account' : 'Login'}
        </button>
        </div>
        </section>
      </motion.div>
    </div>
  )
}
