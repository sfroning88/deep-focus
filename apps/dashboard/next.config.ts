import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  // Monorepo: trace files from repo root (see output caveats in Next.js docs).
  outputFileTracingRoot: path.join(process.cwd(), "../.."),
};

export default nextConfig;
