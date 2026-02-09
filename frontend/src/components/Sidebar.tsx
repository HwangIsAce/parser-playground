'use client'

import React from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'

interface MenuItem {
  name: string
  href: string
  icon: React.ReactNode
  active?: boolean
  disabled?: boolean
}

export default function Sidebar() {
  const pathname = usePathname()

  const menuItems: MenuItem[] = [
    {
      name: 'Parsing',
      href: '/',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      active: pathname === '/' || pathname.startsWith('/documents'),
    },
    {
      name: 'Chunking',
      href: '/chunking',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      ),
      active: pathname === '/chunking' || pathname.startsWith('/chunking/'),
    },
  ]

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-gray-200 border-r border-gray-300 flex flex-col">
      {/* Logo/Title */}
      <div className="p-6 border-b border-gray-300">
        <h1 className="text-xl font-bold text-gray-900">Playground</h1>
      </div>

      {/* Menu */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.name}
              href={item.disabled ? '#' : item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-all
                ${
                  item.disabled
                    ? 'opacity-50 cursor-not-allowed text-gray-500'
                    : item.active
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-300'
                }
              `}
              onClick={(e) => {
                if (item.disabled) {
                  e.preventDefault()
                }
              }}
            >
              {item.icon}
              <span className="font-medium">{item.name}</span>
              {item.disabled && (
                <span className="ml-auto text-xs text-gray-500">Coming soon</span>
              )}
            </Link>
          ))}
        </div>
      </nav>
    </aside>
  )
}
