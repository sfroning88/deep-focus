import Link from "next/link";
import { routes } from "@lib/routes";

export default function AdminPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        Admin
      </h1>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">
        Platform admin tools live here. Add CRUD and management UI as you build
        them out.
      </p>
      <Link
        href={routes.root}
        className="w-fit text-sm font-medium text-zinc-900 underline underline-offset-4 dark:text-zinc-100"
      >
        Back to home
      </Link>
    </div>
  );
}
