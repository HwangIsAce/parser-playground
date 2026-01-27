import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Forge Playground',
  description: 'Document parsing and extraction playground',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
