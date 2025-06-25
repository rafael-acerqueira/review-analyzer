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
    <div>
      <aside className="fixed top-0 left-0 h-screen w-64 bg-white dark:bg-gray-800 shadow-lg flex flex-col justify-between z-30">
        <nav className="mt-8 flex-1 flex flex-col gap-1 overflow-y-auto px-2">
          {visibleLinks.map(link => (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-6 py-3 my-1 rounded-xl text-lg font-medium
                ${pathname === link.href ? 'bg-blue-900 text-white dark:bg-blue-700' : 'text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'}
              `}
            >
              <span className="text-xl">{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="px-6 pb-6">
          <div className="flex items-center gap-2 mb-2">
            <FaUserCircle className="text-2xl text-gray-500" />
            <span className="text-base text-gray-700 dark:text-gray-200 font-medium">
              {session?.user?.email || 'User'}
            </span>
          </div>
          <LogoutButton />
        </div>
      </aside>

      <main className="ml-64 min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        {children}
      </main>
    </div>
  )
}
