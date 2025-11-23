/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  /**
   * Allow local devices hitting the dev server via LAN IP.
   * Prevents upcoming Next.js versions from blocking the origin.
   */
  allowedDevOrigins: ['http://192.168.5.244:3000'],
};

export default nextConfig;
