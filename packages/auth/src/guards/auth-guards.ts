import { cache } from "react";
import { redirect } from "next/navigation";
import { db } from "@focus/db";
import { UserService } from "@focus/services";
import { getSession } from "./session";
import { authRoutes } from "../routes";

export const requirePlatformAdmin = cache(
  async function requirePlatformAdmin() {
    const { supabaseUser } = await getSession();
    if (!supabaseUser) redirect(authRoutes.auth.login);
    await UserService.ensureAppUserFromSupabaseAuth(supabaseUser);
    const appUser = await db.user.findUnique({
      where: { id: supabaseUser.id },
    });
    if (!appUser) redirect(authRoutes.auth.login);
    if (!appUser.isPlatformAdmin) {
      redirect(authRoutes.noAccess);
    }
    return {
      supabaseUser,
      appUser,
    };
  },
);

export const requireUser = cache(async function requireUser() {
  const { supabaseUser } = await getSession();
  if (!supabaseUser) redirect(authRoutes.auth.login);
  await UserService.ensureAppUserFromSupabaseAuth(supabaseUser);
  return {
    supabaseUser,
  };
});
