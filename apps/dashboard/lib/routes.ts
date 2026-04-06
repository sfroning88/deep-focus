import { authRoutes } from "@focus/auth";

export const routes = {
  ...authRoutes,
  admin: {
    root: "/admin" as const,
    org: (orgSlug: string) => `/admin/${orgSlug}` as const,
  },
} as const;
