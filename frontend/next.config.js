/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backend = process.env.NEXT_PUBLIC_API_URL || 'http://194.68.245.19:8000'
    return [
      { source: '/api/v1/:path*', destination: `${backend}/api/v1/:path*` },
    ]
  },
}

module.exports = nextConfig
