# Deep Focus

Portal + AI system for **senior healthcare investing** deployed to [deep-focus.vercel.app](https://deep-focus.vercel.app) with [Next.js](https://nextjs.org) project bootstrapped with [create-next-app](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

**Like what you see? Reach out!** I'll spare you from the [**LinkedIn**](https://www.linkedin.com/in/sean-froning/) bio, but I'm always looking to apply full stack AI to problems that actually matter for people.

## Libraries

This application uses lightweight and free `libraries`:

- `Tailwind colors` -- see official documentation at [tailwindcss.com/docs/colors](https://tailwindcss.com/docs/colors)
- `Lucide React` -- see the official documentation at [lucide.dev/icons/](https://lucide.dev/icons/)
- `React Icons` -- see the official documentation at [react-icons.github.io/react-icons/](https://react-icons.github.io/react-icons/)
- `Sonner Toast` -- see the official documentation at [ui.shadcn.com/docs/components/radix/sonner](https://ui.shadcn.com/docs/components/radix/sonner)

## Database

[`@focus/db`](packages/db) — Prisma 7 + PostgreSQL. Config and migrations live under [`packages/db`](packages/db): [`prisma.config.ts`](packages/db/prisma.config.ts) points at the `prisma/` schema folder and `prisma/migrations/`. CLI uses **`DIRECT_URL`** (direct Postgres; pooled `DATABASE_URL` is for the app client — see [`.env.example`](.env.example)). Use one **repo-root `.env`** and symlink it into `packages/db` (see [Environment](#environment)) so Prisma picks up `DIRECT_URL`.

Supabase **Auth** lives in `auth.users`; app profiles are **`iam.users`** with the same UUID. A trigger (`on_auth_user_created`) is defined in [`20260414000000_on_auth_user_created/migration.sql`](packages/db/prisma/migrations/20260414000000_on_auth_user_created/migration.sql) so it ships with `migrate deploy`; if that migration cannot run against `auth` from your CLI role, apply the same SQL in the Supabase SQL Editor, then mark the migration resolved (see comments in that file).

**From repo root:**

- `pnpm db:generate` — regenerate the Prisma client after schema changes.
- `pnpm db:migrate <migration_name>` — creates `prisma/migrations/` via [`create-migration.sh`](packages/db/prisma/scripts/create-migration.sh) (`prisma migrate dev --create-only --name …`; **does not apply** to any database). Example: `pnpm db:migrate init`. Extra Prisma flags after `--`: `pnpm db:migrate init -- --skip-generate`. Production applies on merge to `main` via [`deploy-db-with-prisma`](.github/workflows/deploy-db-with-prisma.yml) (`migrate deploy`).
- `pnpm db:deploy` — apply pending migrations (`prisma migrate deploy`) using whatever database URLs are in your current `.env` (e.g. local testing against your Supabase project).
- `pnpm run db:prisma <prisma-args>` — run the Prisma CLI from `@focus/db` (e.g. `pnpm run db:prisma migrate resolve --rolled-back 20260414000000_on_auth_user_created`). Do not run bare `pnpm prisma` at the repo root; the binary lives only in that workspace package.
- `pnpm db:studio` · `pnpm --filter @focus/db db:push`

```ts
import { db } from "@focus/db";

await db.user.findMany();
```

Initial migration from an empty DB (run with cwd `packages/db` or via `pnpm --filter @focus/db exec …`):

```bash
npx prisma migrate diff --from-empty --to-schema-datamodel ./prisma --script -o prisma/migrations/__init__/migration.sql
```

## Environment

There is a **single** environment file at the repo root: copy [`.env.example`](.env.example) to `.env` and fill in values. No separate dev/prod env switching in `package.json`—Vercel and GitHub Actions inject their own secrets in deploy.

Point apps and Prisma at that file with symlinks:

```sh
ln -sf ../../.env apps/dashboard/.env
ln -sf ../../.env apps/backend/.env
ln -sf ../../.env apps/ai/.env
ln -sf ../../.env packages/db/.env
```

## Analytics

This application uses a single **anonymous** cookie to track general web analytics using [**PostHog**](https://posthog.com/). Tracking is only used for page visits and basic events.

## Disclaimer

Background music uses the [YouTube IFrame API](https://developers.google.com/youtube/iframe_api_reference); video credits belong to their respective rights holders.

## License

```md
MIT License

Copyright (c) 2025 Sean Froning
```
