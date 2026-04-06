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

[`@focus/db`](packages/db) — Prisma 7 + PostgreSQL. Config and migrations live under [`packages/db`](packages/db): [`prisma.config.ts`](packages/db/prisma.config.ts) points at the `prisma/` schema folder and `prisma/migrations/`. CLI uses **`DIRECT_URL`** (direct Postgres; pooled `DATABASE_URL` is for the app client — see [`.env.example`](.env.example)). Put a **`packages/db/.env`** with at least `DIRECT_URL` when running Prisma commands locally.

**From repo root:** `pnpm db:generate` · `pnpm db:migrate` (`prisma migrate dev`) · `pnpm db:migrate:create -- <name>` (writes `prisma/migrations/<name>/migration.sql` from a schema diff; prints `yes`/`no`) · `pnpm db:deploy:dev` · `pnpm db:studio` · `pnpm --filter @focus/db db:push`

```ts
import { db } from "@focus/db";

await db.user.findMany();
```

Initial migration from an empty DB (run with cwd `packages/db` or via `pnpm --filter @focus/db exec …`):

```bash
npx prisma migrate diff --from-empty --to-schema-datamodel ./prisma --script -o prisma/migrations/__init__/migration.sql
```

## Environment

Create symbolic links to each app:

```sh
ln -sf ../../.env apps/dashboard/.env
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
