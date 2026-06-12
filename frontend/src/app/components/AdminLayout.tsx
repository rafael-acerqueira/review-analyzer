'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FaChartPie, FaTable, FaHome, FaUserCircle, FaCommentDots } from 'react-icons/fa'
import LogoutButton from '@/app/review/components/LogoutButton'
import { useSession } from 'next-auth/react'
import { useEffect, useState } from 'react'

const navLinks = [
  { href: '/', label: 'New Review', icon: <FaCommentDots />, role: 'user' },
  { href: '/my-reviews', label: 'My Reviews', icon: <FaHome />, role: 'user' },
  { href: '/admin/dashboard', label: 'Dashboard', icon: <FaChartPie />, role: 'admin' },
  { href: '/admin', label: 'Reviews', icon: <FaTable />, role: 'admin' },
]

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { data: session } = useSession()
  const [mounted, setMounted] = useState(false)


  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  const visibleLinks = session?.user?.role == 'admin'
    ? navLinks
    : navLinks.filter(link => link.role == 'user')

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-slate-100 lg:grid lg:grid-cols-[17rem_minmax(0,1fr)]">
      <aside className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 lg:sticky lg:top-0 lg:h-screen lg:border-b-0 lg:border-r">
        <div className="flex h-full flex-col">
          <div className="border-b border-slate-200 px-5 py-5 dark:border-slate-800">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Review Analyzer
            </p>
            <p className="mt-1 text-lg font-semibold text-slate-950 dark:text-white">
              Workspace
            </p>
          </div>

          <nav className="flex gap-2 overflow-x-auto px-4 py-3 lg:flex-1 lg:flex-col lg:gap-1 lg:overflow-y-auto lg:px-3">
            {visibleLinks.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className={`inline-flex min-h-11 shrink-0 items-center gap-3 border px-4 py-2 text-sm font-semibold transition lg:w-full
                ${pathname === link.href
                    ? 'border-slate-950 bg-slate-950 text-white dark:border-white dark:bg-white dark:text-slate-950'
                    : 'border-transparent text-slate-600 hover:border-slate-200 hover:bg-slate-50 hover:text-slate-950 dark:text-slate-300 dark:hover:border-slate-800 dark:hover:bg-slate-950 dark:hover:text-white'}
              `}
              >
                <span className="text-base">{link.icon}</span>
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="border-t border-slate-200 px-5 py-4 dark:border-slate-800">
            <div className="mb-3 flex items-center gap-3">
              <FaUserCircle className="text-xl text-slate-500" />
              <span className="min-w-0 truncate text-sm font-medium text-slate-700 dark:text-slate-200">
                {session?.user?.email || 'User'}
              </span>
            </div>
            <LogoutButton />
          </div>
        </div>
      </aside>

      <main className="min-w-0">
        {children}
      </main>
    </div>
  )
}
