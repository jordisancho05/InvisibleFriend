# Domain Analysis Protocol — from goal to usecase + files

> Used by the `planner` skill before writing the plan. Turns a goal into: a **usecase**, the affected
> **layer/files** and the applicable **gotchas**, which feed the GRAPH STEPS.

## Step 1 — Classify the `usecase`
- **assignment** — the Secret Santa algorithm, restriction rules, cycle validation, the domain
  entities. Files: `services/secret_santa.py`, `validators.py`, `models.py`.
- **email** — composing and sending the assignment emails, message copy. Files:
  `services/email_service.py`, `templates/email_template.py`.
- **config** — participants and forbidden pairs (YAML), secrets (`.env`), config parsing and its
  errors. Files: `config.py`, `config/settings.yaml` (+ its `.example`), `.env.example`.
- **general** — cross-cutting: entry point (`main.py`), `utils/` (logger, file_handler), packaging
  (`pyproject.toml`), CI (`.github/workflows/`), docs (`README.md`, `CLAUDE.md`, `CHANGELOG.md`),
  tooling, versioning, project layout.
If it spans several, pick the **main domain** of the change; if purely cross-cutting, `general`.

## Step 2 — Locate the layer (use `project-architecture.md` + `project-tree.md`)
Flow order: `config` (YAML + env) → `models` + `validators` (pure domain) → `services/secret_santa`
(assignment) → `templates` + `services/email_service` (delivery) → `main.py` (orchestration), with
`utils/` cross-cutting. Map each subtask to its layer and to a concrete file (existing or `(NEW)`).
Dependencies point **downward only** — a subtask that makes `validators.py` import a service is a
design error, not an implementation detail.

## Step 3 — Common workflows
If the change matches a common recipe (add a YAML config key, add a secret/env var, change the
assignment or restriction rules, change the email template, add a CLI flag, bump the version), load
`@.claude/skills/references/common-workflows.md` and apply its steps. That file is the single source —
don't restate its steps here.

## Step 4 — Gotchas to flag in the steps
- Flag the **`CLAUDE.md` "Always Remember"** gotchas the affected files hit (always in context — don't
  restate the list): secrets and participants' personal data stay out of git, Spanish user-facing copy
  vs English code, real email sending is opt-in.
- **Domain invariants** any `assignment` step must preserve (see `project-architecture.md`
  §Invariants): the result is a **single cycle** (no fixed points, no sub-cycles), restrictions are
  **symmetric**, and a stricter rule may make the problem unsatisfiable → plan the `AssignmentError`
  path too.
- **Randomness**: `generate_assignments()` shuffles. Any step touching it must be pinned by
  *invariant* tests or a seeded `random`, never by one hard-coded expected mapping.
- **Personal data**: real participant names/emails live only in the gitignored `config/settings.yaml`,
  `output/` and `logs/`. Plans, tests, fixtures and docs use **fake names** (Alice/Bob/…).
- Code-style additions live in `@.claude/skills/implementer/references/execution-rules.md` (type
  hints, `logging` not `print` for new code, config read through the `Config` object).

## Protocol output
1. Chosen `usecase` (justified in one line).
2. List of candidate components/files per subtask (layer + file + function/pattern).
3. Applicable gotchas.
This carries over to each GRAPH STEP's `How` and to the `Plan references` section.
