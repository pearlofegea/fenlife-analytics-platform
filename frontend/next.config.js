/** @type {import('next').NextConfig} */

const rawApiUrl =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://fenlife-analytics-platform-production.up.railway.app";

const apiUrl = rawApiUrl.startsWith("http")
  ? rawApiUrl
  : `https://${rawApiUrl}`;

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
