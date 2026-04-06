import Link from "next/link";
import { db } from "@focus/db";
import { requireUser } from "@focus/auth/server";
import { routes } from "@lib/routes";

export default async function HomePage() {
  const { supabaseUser } = await requireUser();
  const appUser = await db.user.findUnique({
    where: { id: supabaseUser.id },
    select: { email: true, name: true, isPlatformAdmin: true },
  });
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          You are signed in. CRUD and other mutations should run inside{" "}
          <code className="rounded bg-zinc-200 px-1 dark:bg-zinc-800">
            selfUserAction
          </code>{" "}
          server actions.
        </p>
      </div>
      <dl className="grid gap-2 rounded-lg border border-zinc-200 bg-white p-4 text-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div>
          <dt className="text-zinc-500">Name</dt>
          <dd className="font-medium text-zinc-900 dark:text-zinc-100">
            {appUser?.name}
          </dd>
        </div>
        <div>
          <dt className="text-zinc-500">Email</dt>
          <dd className="font-medium text-zinc-900 dark:text-zinc-100">
            {appUser?.email}
          </dd>
        </div>
        <div>
          <dt className="text-zinc-500">Platform admin</dt>
          <dd className="font-medium text-zinc-900 dark:text-zinc-100">
            {appUser?.isPlatformAdmin ? "Yes" : "No"}
          </dd>
        </div>
      </dl>
      {appUser?.isPlatformAdmin ? (
        <Link
          href={routes.admin.root}
          className="inline-flex w-fit text-sm font-medium text-zinc-900 underline underline-offset-4 dark:text-zinc-100"
        >
          Open admin
        </Link>
      ) : null}
    </div>
  );
}
