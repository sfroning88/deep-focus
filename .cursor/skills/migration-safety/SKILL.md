# Prisma migration safety

## What we mean

- **Operational safety (first run):** On a database whose schema matches the migration’s _expected prior state_, the migration applies cleanly in CI (e.g. `.github/workflows/db-deploy-[prod|dev]`) and does not destroy client data you meant to keep.
- **Idempotency (re-run):** Prisma records applied migrations; the same `migration.sql` is not expected to succeed if executed twice manually. That is normal. Do not conflate “safe for deploy” with “safe to run again.”

## Before you merge

1. **Replacing a column (rename / new semantics):** Add the new column, **backfill with `UPDATE`**, then `DROP` the old column. Dropping first loses data permanently.
2. **Foreign keys:** Drop the old FK before altering the old column; add new FKs after data is valid for the new columns.
3. **Scope:** Do not reference tables that are absent on some targets (e.g. QuickBooks tables on a Ready-only DB). Move unrelated DDL to its own migration or drop accidental `CREATE INDEX` lines.
4. **Already applied:** Editing a migration that has run in an environment does **not** re-execute it. Fix forward with a new migration or a one-off script, or restore and replay from scratch (dev only).

## Common issues

- `CREATE TABLE` / `CREATE INDEX` without `IF NOT EXISTS` when the migration might be applied in messy or branched environments (use judgment; Prisma defaults often omit `IF NOT EXISTS`).
- Replacing assignee / ownership columns without an `UPDATE` mapping from the legacy column.
- Unrelated indexes or tables bundled into an app-specific migration (failures when those relations do not exist).

## Easy fixes

- **Backfill pattern:**

```sql
ALTER TABLE "public"."example" ADD COLUMN "new_id" UUID;
UPDATE "public"."example" SET "new_id" = "old_id" WHERE "old_id" IS NOT NULL;
ALTER TABLE "public"."example" DROP COLUMN "old_id";
```

- **Stray DDL:** Delete or relocate statements that touch schemas your deploy DB does not guarantee (cross-product indexes, other services’ tables).
- **Enum values:** Adding a value is usually safe for existing rows; duplicate `ADD VALUE` on re-run fails—acceptable under Prisma; use `IF NOT EXISTS` only if you intentionally need defensive SQL (Postgres version permitting).

## Partial indexes

Prisma often does not express **partial indexes** correctly in generated SQL. If `prisma migrate diff` produced a partial index, hand-verify the `migration.sql` matches intent, or maintain the index outside Prisma if the generator cannot represent it.
