import { Suspense } from "react";
import Link from "next/link";
import { requireUser } from "@focus/auth/server";
import { fetchPropertiesCached } from "@lib/api/cache/property-cache";
import { PropertyList } from "@/app/(components)/(properties)/PropertyList";
import { PropertyListSkeleton } from "@/app/(components)/(properties)/PropertyListSkeleton";
import { routes } from "@lib/routes";

export default async function HomePage() {
  const { appUser, supabaseUser } = await requireUser();
  const properties = await fetchPropertiesCached(supabaseUser.id);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            {appUser.name} · {appUser.email}
          </p>
        </div>
        {appUser.isPlatformAdmin ? (
          <Link
            href={routes.admin.root}
            className="inline-flex w-fit shrink-0 text-sm font-medium text-zinc-900 underline underline-offset-4 dark:text-zinc-100"
          >
            Open admin
          </Link>
        ) : null}
      </div>
      <Suspense fallback={<PropertyListSkeleton />}>
        <PropertyList initialData={properties} />
      </Suspense>
    </div>
  );
}
