import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  
  // Performance optimizations
  compress: true,
  
  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
  },
  
  // Experimental features for performance
  experimental: {
    optimizePackageImports: ['lucide-react', 'date-fns'],
  },
  
  // Ignore TypeScript errors during build
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Webpack config for react-pdf (browser-only, no canvas issues)
  webpack: (config, { isServer, webpack }) => {
    if (!isServer) {
      // react-pdf needs these fallbacks for browser-only operation
      config.resolve.fallback = {
        ...config.resolve.fallback,
        canvas: false,
        fs: false,
        path: false,
        crypto: false,
        stream: false,
        util: false,
        buffer: false,
        process: false,
      };
    }
    
    return config;
  },
  
  // Turbopack config (empty for now, using webpack for react-pdf compatibility)
  turbopack: {},
};

export default nextConfig;
