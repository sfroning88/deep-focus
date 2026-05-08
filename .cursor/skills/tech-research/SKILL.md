# tech-research

Use this skill whenever the user wants to research an employer (investment firm, tech company, or startup) and assess technical fit for a role or opportunity. Triggers include mentions of a company name plus job opportunity, recruiter outreach, job descriptions, networking context, or any request to analyze fit between the user's engineering/technical background and a prospective employer. Also triggers for phrases like "research this firm for me", "how do I stack up against this JD", "what do I need to know before interviewing at X", "assess my fit for this role", "help me prep for this company", or any combination of firm name plus role context. Always use this skill before responding with company/role research. Do NOT skip this skill for firm research even if the request seems simple.

## Tech Research Skill

Produces a ~2000-word black-and-white printable PDF analyzing employer technical fit for the user. The output links the employer's actual technical stack, business model, and engineering practices to the user's documented background and current Rowan platform context — surfacing stack overlaps, honest gaps, learning priorities, and ATS keywords.

---

## Step 0: Read Reference Files First (REQUIRED — Do Not Skip)

**Before doing anything else**, read the three reference files that ground every judgment in this skill. Do NOT rely on memory or prior session knowledge. Re-read every time — the source files may have changed.

Read these files in full using the Read tool:

1. **`./references/resume.md`** — Sean's current resume. The single source of truth for his roles, projects, skills stack, and education. Use this verbatim when assessing what Sean has shipped, what tools he has used in production, and what claims are defensible on a resume.
2. **`./references/tech-stack.md`** — The Rowan platform tech stack (apps, packages, DB, storage, auth, background jobs, AI/LLM stack, deployment, env). Use this as the **"daily use @ Rowan"** baseline. Tech listed here is a strong signal of familiarity. Tech absent from this file is a genuine gap candidate when comparing against an employer's stack.
3. **`./references/full-stack-ai-engineer.md`** — The polymath domain framework (article: "Full Stack AI Engineer: A Modern Day Polymath"). Use this as the canonical list of full-stack AI domains. Every gap identified during research must be cross-referenced against the domains in this file.

If any file is unreadable, surface that explicitly to the user and ask whether to proceed without it. Never substitute remembered content for the real file.

---

## Career Identity (Shapes Every Judgment Call)

Sean is building toward the archetypal **Founding Engineer / Full Stack AI Polymath**: the single person on a lean team who can own the entire solution — frontend, backend, agents, data infrastructure, financial modeling, and go-to-market technical work — without needing a specialist for each layer. The mental model is Leonardo da Vinci, not a narrowly optimized senior engineer: breadth enables innovation that depth alone cannot.

This identity has direct implications for how to frame gaps and learning priorities:

- A gap in a **foundational full-stack AI capability** (any domain enumerated in `./references/full-stack-ai-engineer.md`) is **high-priority** regardless of whether this specific employer requires it. These are polymath table stakes.
- A gap in a **niche enterprise tool** (specific SaaS integration, legacy stack, compliance framework) is **lower priority** — learnable on the job, not worth frontloading.
- When assessing learnability, ask: _does closing this gap make Sean more capable across many future roles, or just this one?_ Prioritize the former.
- The target employers are **lean startups and investment firms applying full-stack AI to real problems** — not FAANG, not large enterprise. Optimize framing for that context.

**Polymath priority test:** After reading `./references/full-stack-ai-engineer.md`, cross-reference every gap identified during research against the domains it enumerates. If a gap falls inside one of those domains, flag it as a **[Polymath Priority]** gap — relevant beyond this role alone — not just a job-fit gap.

---

## Rowan Platform Stack Context

Sean currently builds on the Rowan monorepo described in `./references/tech-stack.md`. When evaluating an employer's stack, use that file to determine what counts as "familiar" vs "unfamiliar":

- Tech that appears in `./references/tech-stack.md` (in the apps, packages, DB, AI/LLM stack, deployment, or env sections) is **"Daily use @ Rowan"** — strong signal of production familiarity.
- Tech that does **not** appear in `./references/tech-stack.md` and does not appear as a project in `./references/resume.md` is a **genuine gap** vs the employer's requirements.
- Tech that appears only in `./references/resume.md` (older projects, prior roles) is **"Prior project / experience"** — real but not current.
- Tech that is conceptually adjacent to something in `./references/tech-stack.md` (e.g., LangChain vs LlamaIndex/CrewAI; Pinecone vs pgvector; Snowflake vs Postgres) is **"Adjacent (transferable concept)"**.

Do NOT enumerate the Rowan stack inline in this skill or in any draft. Always derive familiarity claims by re-reading `./references/tech-stack.md` at the start of each research session.

---

## Step 1: Gather Opportunity Context

The user must provide at minimum: **firm/company name**. Additionally collect (ask if not provided):

- Recruiter message, LinkedIn DM, or networking note (copy/paste)
- Job description or role blurb
- Role title and level (if known)
- Any specific technologies or tools mentioned

If only the company name is given, ask: _"Can you share the job description, recruiter message, or role blurb? Even a few sentences helps target the analysis."_

If nothing beyond company name is available, proceed with research but note the analysis is based on inferred role context.

---

## Step 2: Web Research (REQUIRED — Do Not Skip)

Use `web_search` to gather **fresh, cited sources only**. Do not rely on training knowledge. Cite a **minimum of 6 sources** inline.

Research targets:

### Business & Model

- Primary business model (AUM, product, revenue model, fund strategy, SaaS, marketplace, etc.)
- Recent transactions, fundraising rounds, press releases, or notable news (last 12–24 months)
- Key clients, verticals, or market positioning

### Technical Stack & Engineering

- GitHub org or repos (search `github.com/<firm>` or `site:github.com <firm>`)
- Job postings (especially eng/data/infra roles) — these reveal stack, tools, and infra preferences
- Engineering blog, tech blog, or Medium/Substack posts from their team
- Open source contributions or libraries published
- API documentation, developer portals, or product technical docs
- LinkedIn tech employee profiles for stack signals (tools, certifications, keywords)

### AI/ML & Data Pipelines

- Any public LLM, AI, or ML tooling mentioned (OpenAI, Anthropic, LangChain, vector DBs, etc.)
- Data warehouse or pipeline tools (Snowflake, dbt, Airflow, Spark, Kafka, etc.)
- Integrations or partner tech (Salesforce, Plaid, Bloomberg, etc.)

### Industry Context

- Key regulatory, compliance, or domain-specific technical knowledge relevant to their industry
- Competitors and how technical differentiation shows up in their positioning

---

## Step 3: Clarifying Questions (After Research, Before Writing)

After completing research, if there are specific technologies or integrations discovered that are material to fit assessment, ask the user targeted questions such as:

- _"Their stack appears to include [X]. Are you familiar with this? Used it in production?"_
- _"The role mentions [Y]. Can you tell me more about your experience there?"_
- _"I see [Z] in their infrastructure. Do you want this framed as a gap or a learning opportunity?"_

Limit to 2–4 targeted questions. Skip if context from the resume/JD is already sufficient.

---

## Step 4: Generate PDF Report (~2000 words body prose)

Use `reportlab` to produce a **black-and-white, printable PDF**. Follow the structure below exactly.

### PDF Design Constraints

- **No color.** All text, borders, backgrounds: black, white, or grayscale only.
- **No emoji.** Replace all emoji with text equivalents: `[+]`, `[-]`, `[!]`.
- **No Unicode subscripts/superscripts.** Use ReportLab `<sub>`/`<super>` tags only.
- **Font stack:** Helvetica (headings/labels) + Times-Roman (body prose). Built-in only — no external fonts.
- **Page size:** Letter (8.5" x 11"). Margins: 0.85" all sides.
- **No tables — ever.** Tables render inconsistently and are banned from the final PDF. Always use indented bullet lists with the `•` character and `--` separators instead.

Example format:

```markdown
Specific services to learn:
• Service X -- which does thing Y
• Service W -- which does thing Z
```

Apply this pattern to every list in the report: stack alignment, gap analysis, ATS keywords, priority rankings, and sources.

- **Page numbers:** Bottom center, format `Page N`.
- **Running header:** Firm name + "| Technical Fit Report" on all pages after page 1.

### ReportLab Implementation Pattern

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, PageBreak
)
import datetime

PAGE_W, PAGE_H = letter
MARGIN = 0.85 * inch

def on_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGIN, PAGE_H - 0.55 * inch,
                      f"{firm_name}  |  Technical Fit Report")
    canvas.line(MARGIN, PAGE_H - 0.60 * inch, PAGE_W - MARGIN, PAGE_H - 0.60 * inch)
    canvas.drawCentredString(PAGE_W / 2, 0.55 * inch, f"Page {doc.page}")
    canvas.restoreState()

def on_first_page(canvas, doc):
    canvas.saveState()
    canvas.drawCentredString(PAGE_W / 2, 0.55 * inch, "Page 1")
    canvas.restoreState()

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=0.85 * inch,
    title=f"{firm_name} — Technical Fit Report"
)

H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=13,
                    spaceAfter=6, spaceBefore=14)
H2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=10.5,
                    spaceAfter=4, spaceBefore=10)
BODY = ParagraphStyle("BODY", fontName="Times-Roman", fontSize=10,
                      spaceAfter=6, leading=14, alignment=4)   # 4 = JUSTIFY
MONO = ParagraphStyle("MONO", fontName="Courier", fontSize=8.5, spaceAfter=4)
CITE = ParagraphStyle("CITE", fontName="Times-Roman", fontSize=8.5,
                      spaceAfter=3, leftIndent=12)
LABEL = ParagraphStyle("LABEL", fontName="Helvetica-Bold", fontSize=9,
                       spaceAfter=2, spaceBefore=6)
ITEM = ParagraphStyle("ITEM", fontName="Times-Roman", fontSize=9,
                      spaceAfter=4, leftIndent=18)
```

---

### Report Section Structure (~2000 words body prose)

**1. Cover Block:**

- Firm name (large, bold), subtitle "Technical Fit Report", role title (if known), date generated.

**2. Firm Overview** (200–250 words)

- Business model, fund/product type, AUM or scale, key verticals.
- Recent notable transactions, fundraising, or press (cited).
- Market positioning and competitive context.
- Why this firm would be interesting to a founder-minded AI engineer.

**3. Technical Stack & Engineering Practices** (400–500 words)

- Inferred or confirmed stack: languages, frameworks, databases, cloud/infra, AI/ML tooling, data pipelines, third-party integrations.
- Development culture signals: open source activity, engineering blog cadence, team size, PR velocity, documentation quality.
- **Stack Overlap Analysis**: Explicitly compare their stack against Sean's Rowan platform stack. Call out each technology by name — do not summarize vaguely. For every major technology in their stack, state whether it is "Daily use @ Rowan", "Prior project/experience", "Adjacent (transferable concept)", or "Gap (not in current stack)".
- **Stack Alignment List**: Render as a bullet list using the `•` character — never a table. Include every major technology found (languages, frameworks, infra, AI/ML tools, data tools, cloud providers, integrations). Aim for 8–12 entries minimum. Format each entry as:

  ```markdown
  • Next.js -- Daily use @ Rowan
  • Kubernetes -- Gap (not in current stack)
  • Flask -- Prior project (Financial Health Chatbot)
  • LangChain -- Adjacent (transferable from LlamaIndex/CrewAI)
  ```

- Cite GitHub, job postings, blog posts, and docs inline as [N].

**4. Gap Analysis & Learning Roadmap** (400–500 words)

This section exists to help Sean make an honest self-assessment and decide what to learn. Write it as a senior engineer advising a junior — direct, specific, no sugarcoating.

- **Confirmed Gaps**: Technologies in their stack with "Gap" signal — not present at Rowan, not used in prior projects. For each gap:
  - Name the technology and what it does in their context.
  - Explain why it exists in their stack (what problem it solves, why experienced teams use it).
  - Flag whether this gap falls inside one of the polymath domains enumerated in `./references/full-stack-ai-engineer.md`. If yes, label it **[Polymath Priority]** — relevant beyond this role alone.
  - Assess learnability: weekend project, month of study, or fundamental paradigm shift?
  - Suggest the most direct path to close the gap (specific docs, project idea, or course).
- **Adjacent Gaps**: Technologies where Sean has conceptual exposure but lacks production depth. Distinguish "I understand the concept" from "I've shipped this to production."
- **Structural Gaps**: Domain knowledge, seniority expectations, or non-technical requirements (certifications, compliance, clearances) that are harder to close quickly.
- **Priority Order**: End with a ranked list of which gaps matter most, ordered by: (1) whether it is a polymath domain gap (always rank higher), (2) likelihood the gap surfaces in interview, (3) ease of closing before outreach, (4) strategic value across future roles beyond this one.

**5. ATS & Keyword Strategy** (150–200 words)

- Extract high-signal keywords from the JD or inferred role context.
- Render as a bullet list using the `•` character — never a table. Format each entry as:

  ```markdown
  • Kubernetes -- Add to resume (learnable via Rowan infra migration)
  • RAG pipelines -- In resume (production use @ Rowan)
  • dbt -- Add to cover letter / outreach
  ```

- Note certifications, tools, or credentials worth highlighting or acquiring.

**6. Sources:**

- Numbered list of all cited URLs with brief description.
- Minimum 6 sources. Format: `[N] URL — description`.

---

## Step 5: PDF Generation Notes

- Save to `/mnt/user-data/outputs/tech_research_<firmname>.pdf`
- Present with `present_files` after generation.
- Install if needed: `pip install reportlab --break-system-packages`

---

## Output Requirements

- File: `/mnt/user-data/outputs/tech_research_<firmname>.pdf`
- Present via `present_files`
- Black and white only — no color, no shading, no images
- Fonts: Helvetica (headings) + Times-Roman (body). Built-in ReportLab only.
- Body prose: ~2000 words
- Printable on US Letter, 0.85-inch margins
- Page numbers on every page; running header on pages 2+
- All sources numbered and cited inline as [N]

---

## Quality Checklist (Before Outputting)

- [ ] All three reference files read at the start: `./references/resume.md`, `./references/tech-stack.md`, `./references/full-stack-ai-engineer.md`
- [ ] No resume/stack/polymath content reproduced from memory — every claim grounded in the reference files
- [ ] Output is a `.pdf` file presented via `present_files`
- [ ] No color — strictly B&W/grayscale
- [ ] No emoji — replaced with `[+]` / `[-]` / `[!]`
- [ ] No external fonts — Helvetica + Times-Roman only
- [ ] Page numbers present on every page
- [ ] Running header on pages 2+
- [ ] At least 6 citations with full URLs in Sources
- [ ] Stack alignment list present in Section 3 (8–12 entries minimum)
- [ ] Gap Analysis section present with per-technology learnability assessment
- [ ] Priority-ordered gap list present at end of Section 4
- [ ] ATS keyword list present in Section 5
- [ ] Rowan platform stack explicitly referenced in stack comparison
- [ ] "Daily use @ Rowan" vs "Gap" signals called out by name
- [ ] Zero tables in the entire PDF — all lists use `•` bullet points with `--` separators
- [ ] Body prose is approximately 2000 words

---

## Error Handling

- No GitHub/engineering sources: note explicitly in Section 3 and rely on job postings + news.
- No JD provided: flag ATS section as "inferred from role/firm context", ask after first draft.
- Very small/obscure firm: use LinkedIn employee profiles, Crunchbase, and press as primaries.
- Always produce the PDF even if research is incomplete — note gaps explicitly in the document.
