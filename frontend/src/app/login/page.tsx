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
        router.push('/')
      }
      setLoading(false)
    } else {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (res.ok) {
        await signIn('credentials', { redirect: false, email, password })
        toast.success('Account created!')
        router.push('/')
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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <Toaster position="top-right" />
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="max-w-md w-full bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6 space-y-5"
      >
        <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-100">
          {mode === 'login' ? 'Login to your account' : 'Create a new account'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            required
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-gray-300 rounded-xl p-3 bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            required
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-gray-300 rounded-xl p-3 bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-900 hover:bg-blue-800 text-white font-semibold py-3 rounded-xl transition disabled:opacity-50"
          >
            {loading ? 'Loading...' : mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        <button
          onClick={() => signIn('google', { callbackUrl: '/' })}
          className="w-full flex items-center justify-center border px-4 py-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100"
        >
          <FcGoogle className="mr-2 text-xl" /> Continue with Google
        </button>

        <div className="text-center text-gray-500 dark:text-gray-400">or</div>

        <button
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          className="w-full flex items-center justify-center border px-4 py-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100"
        >
          {mode === 'login' ? 'Create account' : 'Login'}
        </button>
      </motion.div>
    </div>
  )
}
