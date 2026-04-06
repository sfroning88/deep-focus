import "server-only";

import { db } from "@focus/db";
import type { User as SupabaseAuthUser } from "@supabase/supabase-js";

export const UserService = {
  async ensureAppUserFromSupabaseAuth(
    authUser: SupabaseAuthUser,
  ): Promise<void> {
    const email = authUser.email ?? `${authUser.id}@users.local`;
    const name =
      (typeof authUser.user_metadata?.full_name === "string" &&
        authUser.user_metadata.full_name) ||
      (typeof authUser.user_metadata?.name === "string" &&
        authUser.user_metadata.name) ||
      email.split("@")[0] ||
      "User";
    const phonePlaceholder = `+${authUser.id.replace(/-/g, "")}`;
    await db.user.upsert({
      where: { id: authUser.id },
      create: {
        id: authUser.id,
        email,
        name,
        phone: phonePlaceholder,
      },
      update: {
        email,
        name,
      },
    });
  },
};
