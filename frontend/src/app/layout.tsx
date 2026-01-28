import type { Metadata } from 'next'
import './globals.css'
import Sidebar from '@/components/Sidebar'

export const metadata: Metadata = {
  title: 'Playground',
  description: 'Document parsing and extraction playground',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="flex">
        <Sidebar />
        <main className="flex-1 ml-64 min-h-screen bg-gray-50">
          {children}
        </main>
      </body>
    </html>
  )
}
