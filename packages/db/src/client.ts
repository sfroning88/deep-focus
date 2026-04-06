import { PrismaPg } from "@prisma/adapter-pg";
import { setDefaultResultOrder } from "node:dns";
import { PrismaClient } from "../prisma/src/generated/prisma";

// Prefer IPv4 when resolving Supabase hostnames (avoids some local/CI IPv6 issues).
setDefaultResultOrder("ipv4first");

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

/**
 * Runtime: pooled URL (e.g. Supabase :6543 + pgbouncer). CLI uses DIRECT_URL from prisma.config.ts.
 * @see https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections
 */
function createClient() {
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("DATABASE_URL is not set");
  }
  return new PrismaClient({
    adapter: new PrismaPg({ connectionString: databaseUrl }),
    log: process.env.NODE_ENV === "development" ? ["error", "warn"] : ["error"],
  });
}

export const db = globalForPrisma.prisma ?? createClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = db;
}
