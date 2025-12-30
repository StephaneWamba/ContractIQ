/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  // Ignore TypeScript errors during build
  typescript: {
    ignoreBuildErrors: true,
  },
  // Ignore ESLint errors during build
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Output mode - use dynamic rendering to avoid useSearchParams issues
  output: 'standalone',
  // Enable standalone output for Docker (not needed for Vercel)
  // Vercel handles the build output automatically
  // output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,
  // Optimize webpack for Docker/volume mounts (only in development)
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer && process.env.VERCEL !== '1') {
      // Use polling instead of file watching to avoid ENOMEM issues (Docker only)
      config.watchOptions = {
        poll: 2000, // Poll every 2 seconds
        aggregateTimeout: 500,
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/.next/**',
          '**/dist/**',
          '**/build/**',
          '**/.pnpm-store/**',
        ],
      };
    }
    return config;
  },
}

module.exports = nextConfig

