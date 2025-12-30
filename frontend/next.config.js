/** @type {import('next').NextConfig} */
const nextConfig = {
  // Use standalone output for production (better for Docker/Railway)
  output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100',
  },
  // Enable webpack polling for Docker hot reload (development only)
  webpack: (config, { isServer, dev }) => {
    if (!isServer && dev) {
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300, // Delay before rebuilding once the first file changed
      }
    }
    return config
  },
}

module.exports = nextConfig

