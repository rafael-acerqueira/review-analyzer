'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FaChartPie, FaTable, FaHome, FaUserCircle, FaCommentDots } from 'react-icons/fa'
import LogoutButton from '@/app/review/components/LogoutButton'
import { useSession } from 'next-auth/react'

const navLinks = [
  { href: '/', label: 'New Review', icon: <FaCommentDots />, role: 'user' },
  { href: '/my-reviews', label: 'My Reviews', icon: <FaHome />, role: 'user' },
  { href: '/admin/dashboard', label: 'Dashboard', icon: <FaChartPie />, role: 'admin' },
  { href: '/admin', label: 'Reviews', icon: <FaTable />, role: 'admin' },
]

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { data: session } = useSession()

  const visibleLinks = session?.user?.role == 'admin'
    ? navLinks
    : navLinks.filter(link => link.role == 'user')

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">

      <aside className="w-64 bg-white dark:bg-gray-800 shadow-lg flex flex-col justify-between">
        <nav className="mt-8 space-y-1">
          {visibleLinks.map(link => (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-6 py-3 mx-3 my-1 rounded-xl text-lg font-medium
                ${pathname === link.href ? 'bg-blue-900 text-white dark:bg-blue-700' : 'text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'}
              `}
            >
              <span className="text-xl">{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="mb-8 px-6">
          <div className="flex items-center gap-2 mb-2">
            <FaUserCircle className="text-2xl text-gray-500" />
            <span className="text-base text-gray-700 dark:text-gray-200 font-medium">
              {session?.user?.email || 'User'}
            </span>
          </div>
          <LogoutButton />
        </div>
      </aside>

      <main className="flex-1 p-8">{children}</main>
    </div>
  )
}