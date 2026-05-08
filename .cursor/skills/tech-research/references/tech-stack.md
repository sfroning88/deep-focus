# Rowan Platform — Tech Stack Reference

**This is the single source of truth for the Rowan platform architecture, product surface, and tech stack.**
Both the `tech-stack-integration` and `product-roi` skills (and any other skill that needs to reason about Rowan's stack) should read this file rather than duplicating architecture facts inline.

Always attempt to fetch the repo for the latest state; flag any assumptions if the repo is inaccessible.

---

## 1. Operating System Overview

Rowan is building an **operating system for small business succession** — a platform that lets owners preparing for sale (or buyers preparing to acquire) work from a single source of truth instead of combing paper copies, legacy software, and email chains. The platform is structured around a three-phase data pipeline:

| Phase             | Question                                                           | Worker                                   |
| ----------------- | ------------------------------------------------------------------ | ---------------------------------------- |
| **I. Ingest**     | "Where does messy client data live and how can we fetch it?"       | `ingest-worker`                          |
| **II. Transform** | "How can we turn messy client data into programmably useful data?" | `transform-worker`                       |
| **III. Utilize**  | "How can we visualize and interact with programmably useful data?" | `ready-worker` (+ `apps/ready` frontend) |

The platform unlocks **two complementary data types** in one digestible interface:

- **Relational / Tabular Data** — Spreadsheet-style data with explicit internal linkage (balance sheets, invoices-by-customer, valuation models, sales forecasts). Highly reliable but limited to predictable templates.
- **Prosaic / Semantic Data** — Text-heavy content where meaning depends on document context (market research, news articles, books, call transcripts). Holds the "why" behind numbers but harder to query exactly.

Combining the two — backed by AI/SaaS tooling traditionally unavailable to small industrial businesses — is what lets sellers command top-multiple at exit and lets buyers accelerate diligence post-close.

---

## 2. Monorepo Layout

Turborepo + pnpm workspaces. Workspace globs: `apps/*`, `packages/*`.

```md
rowan-platform/
├── apps/
│ ├── receivables/ # Next.js (Vercel) — receivables.trustrowan.com
│ ├── ready/ # Next.js (Vercel) — ready.trustrowan.com (succession portal)
│ ├── receivables-worker/ # FastAPI (Render) — AR worker
│ ├── ingest-worker/ # FastAPI (Render) — Pipeline Phase I
│ ├── transform-worker/ # FastAPI (Render) — Pipeline Phase II
│ ├── ready-worker/ # FastAPI (Render) — Pipeline Phase III + RAG chat
│ ├── platform-express/ # Express (Render) — integrations, cron, webhooks
│ ├── collect-tool/ # Next.js (Vercel) — embedded lead-gen demo
│ ├── buyer-search-tool/ # Next.js (Vercel) — embedded buyer search
│ └── valuation-tool/ # Next.js (Vercel) — embedded instant valuation
└── packages/
├── auth/ # @rowan/auth (3 subpath exports)
├── iam/ # @rowan/iam (2 subpath exports)
├── db/ # @rowan/db — Prisma schema + client
├── config/ # @rowan/config (Next.js env)
├── config-js/ # @rowan/config-js (Node.js env)
├── types/ # @rowan/types
├── ui/ # @rowan/ui (shadcn-based)
├── utils/ # @rowan/utils
├── services/ # @rowan/services
├── analytics/ # @rowan/analytics (PostHog)
├── tsconfig/ # Shared TypeScript bases
└── python/ # Shared rowan_workers (FastAPI factory, db_pool, redis, storage)
```

---

## 3. Apps

### `apps/receivables/` — Next.js / Vercel

`receivables.trustrowan.com`. AR/collections dashboard synced with QuickBooks Online.

- **Routing:** Org-scoped via `[orgSlug]`
- **Features:** AR dashboard (DSO trends, aging buckets, cash flow), customer management, invoice tracking, collection campaigns with AI-generated outreach, conversational AI agent UI, AR analytics + reports, QBO connection settings
- **Auth/IAM:** `@rowan/auth` + `@rowan/iam`
- **DB access:** Prisma via `@rowan/db`

### `apps/ready/` — Next.js / Vercel

`ready.trustrowan.com`. The **succession portal** for small business owners in M&A due diligence before sale or retirement. Mirrors auth orgs/users via IAM.

- **Routing:** Org-scoped via `[orgSlug]`. `[orgSlug]/page.tsx` checks org type and routes to AdminHome (parent/advisor) or ClientHome (child/client)
- **Dual-view architecture:**
  - **Parent / advisor orgs → AdminHome:** Clients table with sub-org readiness scores. Advisors **link organizations** (onboard a child client org into Ready) and **link users** (add client org members so they receive tasks). This is the new-client onboarding funnel.
  - **Child / client orgs → ClientHome:** Assigned diligence tasks (with video guidance) across **five M&A pillars** — Foundation, People & Operations, Legal & Contracts, Risk & Assets, Technology. Tasks roll up to readiness scores (`CertifiedProgress` bar).
- **Knowledge base:** Org-scoped document library with wiki view, document upload, document viewer. Powered by `knowledge_document` + `knowledge_section` models. Documents become browsable as the data pipeline processes them.
- **RAG chat:** Conversational interface querying the org's embedded document chunks via pgvector similarity search, with source citations rendered inline (`SourceCard` components). Backend handled by `ready-worker`.
- **Task completion:** Tasks include text instructions, video guidance, and optional file upload. Uploads flow through the ingest pipeline; completed `staging_file.id`s are written to `ready_task.file_ids`.
- **Auth/IAM:** `@rowan/auth` + `@rowan/iam`
- **DB access:** Prisma via `@rowan/db`

**Future state (per the Operating System Cheat Sheet):** A system that can intelligently determine which files have been uploaded, which are missing and need to be generated, and link them to completed tasks automatically.

### `apps/receivables-worker/` — FastAPI / Render

Long-running Python worker for the AR product.

- **Integrations:** QuickBooks Online (OAuth + sync via RQ background jobs + webhook), AI collection agents (Perplexity/OpenAI), campaign execution, AR document analysis, automated report generation
- **DB access:** Raw SQL via `psycopg2` connection pool (`rowan_workers.db_pool`)
- **Shared code:** `packages/python` (`rowan_workers`)

### `apps/ingest-worker/` — FastAPI / Render — **Pipeline Phase I**

Connects to third-party data stores via OAuth, downloads raw files, lands them in staging, and enqueues transform jobs.

- **Third-party data stores:** Box, Dropbox (planned), Gmail, Outlook (planned), Custom Portal (manual upload)
- **Fintech software (planned/in-progress):** QuickBooks Online (live), Xero (planned), Gusto (planned), Paychex (planned), NetSuite (planned), SAP (planned)
- **Live integration modules:**
  - `box/` — OAuth, webhook, manual sync for org folders, chunked upload helpers
  - `gmail/` — Pub/Sub push notifications for email/attachments
  - `upload/` — Manual multipart file upload endpoint
  - `quickbooks/` — OAuth, data sync, helpers
- **Endpoints (representative):** `GET /box/authorize`, `GET /box/callback`, `POST /box/webhook`, `POST /box/sync`, `GET /box/status/{org_id}`; `POST /gmail/watch`, `POST /gmail/webhook`; `POST /upload/file`; `GET /quickbooks/authorize`, `GET /quickbooks/callback`, `POST /quickbooks/sync`; `GET /` (health), `GET /rq/jobs`
- **Flow:** Receive event/file → download raw → chunked upload to Supabase `data-staging` bucket → insert `staging_file` row (status `pending`) → enqueue RQ job for transform-worker
- **OAuth tokens:** Stored in `integration_credential` table (`org_id` + `provider` unique). Token refresh handled automatically.
- **DB access:** Raw SQL via `psycopg2`
- **Stack:** Standard `rowan_workers` (psycopg2, Redis/RQ, Supabase storage)

### `apps/transform-worker/` — FastAPI / Render — **Pipeline Phase II**

ETL pipeline: pulls raw files from staging, classifies via LLM, processes by document type, and routes to the correct final destination.

- **Pipelines (`src/pipelines/`):**
  - `text_pipeline.py` — PDF, TXT, DOCX → extract text → chunk → embed → pgvector
  - `spreadsheet_pipeline.py` — XLSX, CSV → parse structured data → validate → relational tables
  - `email_pipeline.py` — Email body + attachments → sub-process each
  - `classifier.py` — LLM-based document type classification
  - `router.py` — Routes files to correct pipeline based on type
- **Services (`src/services/`):** `embedding_services.py` (OpenAI), `extraction_services.py` (PyPDF2, python-docx), `storage_services.py` (final routing), `classification_services.py`
- **Endpoints:** `POST /transform/process`, `POST /transform/batch`, `GET /transform/status/{file_id}`, `POST /transform/reprocess/{file_id}`; `GET /` (health), `GET /rq/jobs`
- **Final destinations:**
  - `document_chunk` table (pgvector embeddings) for RAG
  - Relational Prisma tables (validated tabular data)
  - `data-clean` Supabase bucket (multimodal — images, diagrams)
  - `document-wiki` Supabase bucket (processed document copies for the knowledge base)
- **DB access:** Raw SQL via `psycopg2`
- **Stack:** Standard `rowan_workers`

### `apps/ready-worker/` — FastAPI / Render — **Pipeline Phase III**

Backend API for the Ready product. Powers RAG chat, knowledge base, tasks, scoring, and document management.

- **Modules (`src/integrations/`):**
  - `chat/` — RAG chat orchestration. Services:
    - `retrieval_services.py` — pgvector similarity search filtered by `org_id`
    - `rerank_services.py` — Cohere `rerank-v3.5` (top-20 retrieved → top-5 reranked)
    - `llm_services.py` — Anthropic Claude Sonnet response generation with system prompt enforcing citation + uncertainty acknowledgement
    - `building_services.py` — Pipeline orchestration, conversation context (last ~10 messages), source citation formatting
  - `knowledge/` — Knowledge document CRUD (`knowledge_document`, `knowledge_section`)
  - `tasks/` — Task CRUD, completion (with file linkage), filterable by category/status
  - `scores/` — Readiness score calculation across the five M&A pillars
  - `documents/` — Document management endpoints
- **Endpoints (representative):**
  - Chat: `POST /chat/conversations`, `GET /chat/conversations/{org_id}`, `GET /chat/conversations/{conversation_id}/messages`, `POST /chat/message` (RAG response), `DELETE /chat/conversations/{conversation_id}`
  - Knowledge: `GET /knowledge/{org_id}`, `GET /knowledge/document/{document_id}`, `POST /knowledge/documents`, `PUT /knowledge/document/{document_id}`, `DELETE /knowledge/document/{document_id}`
  - Tasks: `GET /tasks/{org_id}`, `GET /tasks/task/{task_id}`, `POST /tasks`, `PUT /tasks/{task_id}`, `PUT /tasks/{task_id}/complete`, `DELETE /tasks/{task_id}`
  - Scores: `GET /scores/{org_id}`, `GET /scores/{org_id}/pillar/{pillar}`, `POST /scores/{org_id}/recalculate`
  - Documents: `GET /documents/{org_id}`, `GET /documents/document/{document_id}`, `POST /documents/upload`
- **DB access:** Raw SQL via `psycopg2`
- **Stack:** Standard `rowan_workers`

### `apps/platform-express/` — Express (Node.js + TypeScript) / Render

Integrations, cron-style work, and Gmail-adjacent HTTP surface. Follows the **Controller → Action → Service → Prisma** architecture (see `.claude/skills/express-refactor/SKILL.md`).

- **Routes:** `gmail/` (webhook + watch), `hubspot/` (CRM contact/deal sync from trustrowan.com lead capture), `cron/` (scheduled QBO sync triggers, health monitoring), `webhooks/` (generic receiver)
- **Middleware:** API key auth, error handler, request logging
- **Dependencies:** `@rowan/services`, `@rowan/config-js`, `@rowan/types`. `@rowan/db` is a build-time dep; **no runtime Prisma usage yet.**

### `apps/collect-tool/` — Next.js / Vercel

Embedded into trustrowan.com. Lead-gen demo: "send yourself a free collection call." Showcases the AI collections agent (Perplexity + ElevenLabs + Vapi) with strict Redis-backed rate limiting. CSP via `vercel.json`. **No auth.**

### `apps/buyer-search-tool/` — Next.js / Vercel

Embedded into trustrowan.com (`IframeHeightNotifier`). Buyers search for acquisition targets by industry, geography, revenue, employee count. Interactive Leaflet map. Lead capture via HubSpot. Uses `@rowan/db` (Prisma). No Redis. **No auth.**

### `apps/valuation-tool/` — Next.js / Vercel

Embedded into trustrowan.com (`IframeHeightNotifier`). Instant business valuation from a URL — industry multiples, potential acquirers, lead capture funnel. Uses `@rowan/db` (Prisma). No Redis. **No auth.**

---

## 4. Packages

### `packages/auth/` — `@rowan/auth`

Shared Supabase Auth. Three subpath exports prevent barrel-export poisoning:

| Subpath                  | Contains                                                                                                                                                                                                                                                                                                                                                        | Safe for                                                   |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `@rowan/auth`            | Components (login, signup, OAuth buttons), hooks (Google SSO, Outlook SSO, invitation signup), browser Supabase client, routes, constants                                                                                                                                                                                                                       | Client components (`"use client"`)                         |
| `@rowan/auth/server`     | Guards (`requireUser`, `requireOrgAccess`, `requireOrgOwner`, `requirePlatformAdmin`, `requireRowan`), action factories (`createPublicAction`, `selfUserAction`, `orgOwnerAction`, `orgMemberAction`, `platformAdminAction`, `rowanAction`), route handlers (`handleAuthCallback`, `handleResetPassword`), server + admin Supabase clients. Uses `server-only`. | Server components, server actions, layouts, route handlers |
| `@rowan/auth/middleware` | `updateSession` only                                                                                                                                                                                                                                                                                                                                            | Edge Runtime (`middleware.ts`)                             |

**Never** import `/server` from a client component or `middleware.ts`. **Never** import guards/handlers from the root barrel.

### `packages/iam/` — `@rowan/iam`

Shared Identity & Access Management. Two subpath exports: `@rowan/iam` (UI) and `@rowan/iam/server` (actions).

- **Providers:** `QueryProvider`, `SupabaseProvider`, `AuthProvider`, `UserProvider`, `OrgProvider`, `AppProvider` — composed in each app's root `layout.tsx`
- **Components:** `OrgSwitcher`, `UserMenu`, `OrganizationList`, `OrganizationView`, `OrganizationPageStates`, `ViewOrganizationChildren`, `MembersSection`, `InvitationsSection`, `MembersTable`, `ProfileEditModal`, `ChangePasswordModal`, `InviteUserModal`, `UserInviteButton`, `UserInvitations`, `PrivacyPolicy`, `BackButton`, `CreateOrganizationModal`
- **Hooks:** TanStack Query wrappers — `useGetOrganization`, `useGetOrganizations`, `useGetSubOrganizations`, `useGetOrganizationMembers`, `useGetInvitations`, `useCreateSubOrganization`, `useCreateRootOrganization`, `useDeactivateSubOrganization`, `useReactivateSubOrganization`, `useSendInvitation`, `useRevokeInvitation`, `useRemoveUserFromOrganization`, `usePromoteUserMemberToOwner`, `useAddUserToOrganization`, `useUpdateProfileDetails`, `useChangePassword`, `useDeactivateProfile`, `useGetPrivacyPolicy`
- **Constants:** `IAM_QUERY_KEYS`, `QUERY_STALE_TIME`, `FALLBACK_MESSAGE`
- **Reducers:** `authProviderReducer`, `changePasswordFormReducer`, `updatePasswordReducer`, `viewOrgChildrenReducer`, `createOrgModalReducer` (+ initial states)
- **Routes:** `iamRoutes` extends `authRoutes` with `/admin`, `/${orgSlug}/organization`, `/${orgSlug}/users`. Apps extend `iamRoutes` with their own paths.
- **Tailwind:** Apps must include `../../packages/iam/src/**/*.{ts,tsx}` in their `tailwind.config.js` `content`.

**Never duplicate IAM components, hooks, actions, or reducers locally** in an app. Add shared functionality to `packages/iam`.

### `packages/db/` — `@rowan/db`

Prisma client and split schema. `prisma/schema/*.prisma`:

| File                  | Key models                                                                                             | Purpose                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| `user.prisma`         | `user`, `user_profile`                                                                                 | User accounts, profiles                                               |
| `organization.prisma` | `organization`, `organization_member`, `invitation`                                                    | Org hierarchy (parent/child via `parent_id`), membership, invitations |
| `staging.prisma`      | `staging_file`, `document_chunk` (pgvector), `integration_credential`                                  | Pipeline staging, embeddings, OAuth tokens                            |
| `knowledge.prisma`    | `knowledge_document`, `knowledge_section`                                                              | Knowledge base (RAG-backed)                                           |
| `chat.prisma`         | `chat_conversation`, `chat_message`                                                                    | RAG chat conversations + messages (with `sources` JSON)               |
| `ready.prisma`        | `ready_task`, `ready_score`                                                                            | Tasks across five M&A pillars + readiness scores                      |
| `receivables.prisma`  | `customer`, `invoice`, `payment`, `campaign`, `campaign_action`, `agent_conversation`, `agent_message` | AR data, campaigns, AI agents                                         |
| `quickbooks.prisma`   | `qbo_connection`, `qbo_sync_log`                                                                       | QBO OAuth state, sync history                                         |
| `analytics.prisma`    | `analytics_event`, `page_view`                                                                         | Product analytics                                                     |
| `valuation.prisma`    | `valuation_report`, `industry_multiple`                                                                | Valuation tool data                                                   |
| `buyer.prisma`        | `buyer_profile`, `buyer_search`, `acquisition_target`                                                  | Buyer search tool data                                                |
| `lead.prisma`         | `lead`, `lead_activity`                                                                                | Lead capture from embedded tools                                      |

The `organization` model is the hub — it relates to staging files, integration credentials, ready tasks/scores, knowledge documents, chat conversations, customers, campaigns, QBO connection, etc.

**Migration name convention:** `YYYYMMDD_description`.

### `packages/config/` and `packages/config-js/`

`@rowan/config` is the **single source of truth for Next.js environments** (`@t3-oss/env-nextjs`). Mirrors one-to-one in `@rowan/config-js` for the Express service and Python workers' Node-side tooling. Secrets default to **server-only and optional** unless explicitly public-required.

### `packages/python/` — Shared `rowan_workers`

The shared Python package used by all four FastAPI workers.

- `app.py` — `create_app()` FastAPI factory (CORS, health route, RQ routes, middleware)
- `db_pool.py` — `psycopg2` connection pool, `get_db_connection()` context manager
- `redis_client.py` — Redis connection from `REDIS_URL`, `get_queue(name)` factory
- `storage.py` — Supabase Storage helpers: `upload_file`, `download_file`, `list_files`, `delete_file`, `get_public_url`. Buckets: `data-staging`, `data-clean`, `document-wiki`
- `config.py` — Centralizes env vars (`DATABASE_URL`, `REDIS_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)
- `middleware.py` — Request logging, error handling
- `rq_routes.py` — Shared RQ job status/management endpoints
- `exceptions.py` — Custom exception classes

**Named RQ queues:** `default`, `ingest`, `transform`, `ready`.

### Other shared packages

- `packages/types/` — `@rowan/types` (repo-wide TypeScript types)
- `packages/ui/` — `@rowan/ui` (shadcn-based components)
- `packages/utils/` — `@rowan/utils` (repo-wide utilities)
- `packages/services/` — `@rowan/services` (shared user-facing services)
- `packages/analytics/` — `@rowan/analytics` (PostHog setup)
- `packages/tsconfig/` — Shared TypeScript config bases

---

## 5. Database

**PostgreSQL (Supabase-hosted) with pgvector** for embeddings. Two access patterns:

- **TypeScript apps:** **Prisma** via `@rowan/db` (`packages/db/prisma/schema/*.prisma` + `migrations/`)
- **Python workers** (`receivables-worker`, `ingest-worker`, `transform-worker`, `ready-worker`): **Raw SQL** via a `psycopg2` connection pool (`rowan_workers.db_pool`), connecting via `DATABASE_URL` directly
- **`platform-express`:** `@rowan/db` is a build dependency only — no runtime Prisma usage

**No RLS policies are tracked in this repo.** Authorization happens at the application layer via `@rowan/auth` guards. Be alert to **dual-write risk** between Prisma (TS) and psycopg2 (Python) on the same tables.

---

## 6. Storage (Supabase Buckets)

| Bucket          | Purpose                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------ |
| `data-staging`  | Raw ingested files immediately after upload from any source. Lookup row in `staging_file` table. |
| `data-clean`    | Processed multimodal files (images, diagrams) after transform.                                   |
| `document-wiki` | Processed document copies powering the Ready knowledge base / wiki.                              |

---

## 7. Auth

**Supabase Auth** managed via the shared `@rowan/auth` package. Auth is **never app-local** — `receivables` and `ready` both import from the shared package. The three tool apps (`collect-tool`, `buyer-search-tool`, `valuation-tool`) do **not** use auth.

- **SSO:** Google (`provider: "google"`) and Azure/Outlook (`provider: "azure"`) via Supabase OAuth. Provider config (client IDs, secrets, redirect URLs) lives in the **Supabase project dashboard**, not the codebase. App code only references the callback URL `/auth/callback`. Adding a new SSO provider follows the same Supabase OAuth pattern.
- **Identity join:** Supabase `user.id` maps 1:1 to Prisma `db.user.id`. Guards call `supabase.auth.getUser()`, then verify against Prisma for org membership, roles, activation status.
- **Python workers** authenticate to Postgres via `DATABASE_URL` (connection string), not the Supabase service role.

---

## 8. Background Work / Redis

Job queuing via **RQ** in all four Python workers. Named queues: `default`, `ingest`, `transform`, `ready`. Redis is also used for **rate limiting** in `collect-tool`. Any new integration that involves long-running work or rate limits should assume `REDIS_URL` is required.

---

## 9. Data Pipeline (End-to-End)

```md
┌─────────────────────────────────────────────────────────────────┐
│ DATA SOURCES │
│ Box │ Gmail │ Manual Upload │ QuickBooks │ (future) │
└───┬───┴────┬────┴───────┬─────────┴──────┬───────┴──────────────┘
│ │ │ │
▼ ▼ ▼ ▼
┌─────────────────────────────────────────────────────────────────┐
│ INGEST WORKER (FastAPI / Render) │
│ OAuth (integration_credential) │ Webhooks │ Manual upload │
│ → Upload raw to "data-staging" Supabase bucket │
│ → Insert staging_file row (status: pending) │
│ → Enqueue RQ job for transform │
└─────────────────────────────────┬───────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ TRANSFORM WORKER (FastAPI / Render) │
│ 1. Fetch raw file from data-staging │
│ 2. LLM classification (doc_type) │
│ 3. Route to pipeline: │
│ • Text → extract → chunk → embed (OpenAI) → pgvector │
│ • Spreadsheet→ parse → validate → relational tables │
│ • Email → parse body + attachments → sub-process │
│ 4. Store to final destination: │
│ • document_chunk table (pgvector embeddings) │
│ • Relational Prisma tables │
│ • data-clean bucket (multimodal) │
│ • document-wiki bucket (wiki copies) │
│ 5. Update staging_file.status → completed/failed │
└─────────────────────────────────┬───────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ READY WORKER (FastAPI / Render) │
│ RAG Chat: query → embed → pgvector search → │
│ Cohere rerank-v3.5 → Anthropic Claude → │
│ response with source citations │
│ Knowledge Base CRUD (knowledge_document + knowledge_section) │
│ Tasks + Readiness scoring across the five M&A pillars │
└─────────────────────────────────┬───────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ READY FRONTEND (Next.js / Vercel) │
│ AdminHome (parent orgs) │ ClientHome (child orgs) │
│ Tasks │ Scores │ Knowledge Base │ Chat (RAG) │
└─────────────────────────────────────────────────────────────────┘
```

**Key models touching the pipeline:** `staging_file`, `document_chunk` (pgvector), `integration_credential`, `knowledge_document`, `knowledge_section`, `chat_conversation`, `chat_message`, `ready_task`, `ready_score`.

**How Ready connects to the pipeline:**

1. User uploads a file via Ready (task completion or knowledge base upload)
2. Next.js API route proxies to `ingest-worker POST /upload/file`
3. Ingest worker stores raw in `data-staging`, creates `staging_file`, enqueues RQ job
4. Transform worker processes → chunks → embeddings stored in `document_chunk`
5. If part of a task completion, `staging_file.id` is appended to `ready_task.file_ids`
6. `knowledge_document` record created/linked
7. Document becomes queryable via RAG chat

---

## 10. AI / LLM Stack

| Layer                   | Model / Service                                                               | Used in                                          |
| ----------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------ |
| Embeddings              | OpenAI `text-embedding-3-small` (1536 dims, pgvector)                         | transform-worker, ready-worker (query embedding) |
| RAG LLM                 | Anthropic Claude Sonnet (with system prompt enforcing citation + uncertainty) | ready-worker `llm_services.py`                   |
| Reranker                | Cohere `rerank-v3.5` (top-20 → top-5)                                         | ready-worker `rerank_services.py`                |
| Document classification | LLM classifier                                                                | transform-worker `classifier.py`                 |
| Collection agents       | Perplexity + OpenAI                                                           | receivables-worker                               |
| Voice                   | ElevenLabs (synthesis) + Vapi (voice agent platform)                          | collect-tool demo                                |

**RAG pipeline configuration:** Top-20 chunks retrieved → reranked to top-5 → context window includes last ~10 messages from conversation → response streamed to client with `sources` JSON stored on the `chat_message` row.

**Where to add new LLM/agent features:** The appropriate Python worker (usually `ready-worker` or `transform-worker`) unless the capability is strictly frontend-only.

---

## 11. Deployment

- **Vercel** (Next.js, serverless / edge-oriented; no long-running processes): `receivables`, `ready`, `collect-tool`, `buyer-search-tool`, `valuation-tool`
- **Render** (always-on backends): `receivables-worker`, `ingest-worker`, `transform-worker`, `ready-worker`, `platform-express`
- **Embedded apps** (`collect-tool`, `buyer-search-tool`, `valuation-tool`) embed into `trustrowan.com`. CSP headers configured in each app's `vercel.json`. Iframe-embeddable apps use `IframeHeightNotifier` — audit `postMessage` origins when modifying.
- **Database:** Supabase-hosted PostgreSQL (single project, single DB)
- **Storage:** Supabase Storage (3 buckets — see §6)
- **Redis:** Single managed Redis (Render or external) used by all Python workers + collect-tool rate limiting

---

## 12. Environment & Secrets

- **Root files:** `.env.local`, `.env.dev`, `.env.prod`
- **`pnpm use:local` / `use:dev` / `use:prod`** copies the selected file to the repo root `.env` (see `scripts/env-setup.js`)
- **Per-app `.env`:** Each app has a symlink from `.env` → `../../.env` so local runs resolve the same root profile. Next.js builds also load root `.env` via `dotenv` in scripts where configured.

**Key environment variables:**

| Variable                                                     | Purpose                                     |
| ------------------------------------------------------------ | ------------------------------------------- |
| `DATABASE_URL`                                               | Supabase PostgreSQL connection string       |
| `DIRECT_URL`                                                 | Direct PG connection for Prisma migrations  |
| `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase client config                      |
| `SUPABASE_SERVICE_ROLE_KEY`                                  | Service role for backend writes             |
| `REDIS_URL`                                                  | Redis (RQ + rate limiting)                  |
| `OPENAI_API_KEY`                                             | Embeddings + collection agents              |
| `ANTHROPIC_API_KEY`                                          | Claude (RAG response)                       |
| `COHERE_API_KEY`                                             | Reranking                                   |
| `QBO_CLIENT_ID` / `QBO_CLIENT_SECRET`                        | QuickBooks OAuth                            |
| `BOX_CLIENT_ID` / `BOX_CLIENT_SECRET`                        | Box OAuth                                   |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`                  | Gmail OAuth (for ingest, separate from SSO) |
| `HUBSPOT_API_KEY`                                            | HubSpot CRM integration                     |
| `POSTHOG_API_KEY`                                            | Analytics                                   |
| `ELEVENLABS_API_KEY`                                         | Voice synthesis                             |
| `VAPI_API_KEY`                                               | Voice agent platform                        |

---

## 13. App Boundary Decision Rules

When evaluating a new integration or feature, place it in the **smallest deployable that owns the concern**:

- **Frontend UI only?** → Relevant Next.js app (`receivables`, `ready`, embedded tool)
- **Long-running background work, OAuth-heavy integrations, LLM/agent calls?** → A Python worker (`ingest-worker` for new data sources, `transform-worker` for new processing pipelines, `ready-worker` for new utilization features, `receivables-worker` for AR-specific work)
- **Cron / webhook receivers / Gmail-adjacent HTTP?** → `platform-express`
- **Shared across apps (auth, IAM, types, UI, env, services)?** → `packages/`
- **Genuinely new product surface with its own scaling/deployment cadence and subdomain?** → New `apps/` entry, justified explicitly (Render/Vercel config, Turborepo pipeline registration, pnpm workspace entry)

**Cross-app risks to watch:** dual-write between Prisma (TS) and psycopg2 (Python) on the same tables; tight coupling that prevents independent deploys; distributed transaction risk; changes to `packages/auth` or `packages/iam` that propagate to every authenticated app.

---

## 14. Default Team Scale Context

- Small team (~2 engineers), full-stack ownership
- Monorepo with multiple Vercel frontends, four Render Python workers, one Render Express service, one Supabase/Postgres project, one Redis instance
- Shared `@rowan/auth` and `@rowan/iam` — changes propagate across all authenticated apps
- Core priority: **product velocity and reliability over infrastructure sophistication**
- Every integration must justify its maintenance burden in a small-team context
