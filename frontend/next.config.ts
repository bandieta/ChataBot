import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  basePath: "/ChataBot",
  trailingSlash: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8001/:path*",
      },
    ];
  },
};

export default nextConfig;
