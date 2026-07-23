---
name: pr-review
description: Review a PR / diff against this project's rules and gotchas. Use when the user says "revisa esta PR", "revisa los cambios", "code review".
---

# pr-review

Review changes against `CLAUDE.md`. The deep, itemized checklist lives in
`references/checklist-deep.md`; the skill's behavior is validated by `evals/evals.json`.

## Procedure
1. **Get the diff.** If not provided, ask for it (or `git diff <base>...<head>`).
2. **Scope it.** Identify the touched usecases (`assignment`, `email`, `config`, `general`:
   entry point / packaging / docs / tooling). Only the matching checklist sections apply.
3. **Run the checklist** in `references/checklist-deep.md` (privacy & secrets → domain invariants →
   config → email → languages → layering & style → tests → packaging/versioning → hygiene). Load it
   on demand.
4. **Report** the structured summary below; each finding cites `file:line` and the rule it breaks.

## Output
Structured summary (omit empty buckets):
- ❌ Blockers — must fix before merge: a real secret or a **real participant's name/email** in the
  diff; a versioned `.env` / `config/settings.yaml`; a broken domain invariant (the assignment stops
  being a single cycle, restrictions stop being symmetric); a default that sends email; a test that
  opens a socket or reads the real config; changed behavior with no test.
- ⚠️ Warnings — should fix: convention break with contained impact (`os.getenv` or a second
  `yaml.safe_load` outside `Config`, `print` instead of `logging` inside the package, a bare
  `Exception` or an unchained `raise`, a layering violation, a missing type hint, an assignment test
  asserting one fixed mapping instead of invariants). Always state the risk.
- ✅ Recommendations — optional improvements: style, structure, small refactors; no rule broken.

## References (load on demand)
- `references/checklist-deep.md` — full itemized review checklist (rules, gotchas, tests).
- `@.claude/skills/references/project-architecture.md` — layer/module map + invariants (only if scope
  is unclear).
- `@.claude/skills/references/common-workflows.md` — the recipe the change should have followed.

## Evals
`evals/evals.json` — labeled diff scenarios with the findings each review must catch (plus a clean
negative case). Use it to validate changes to this skill or `checklist-deep.md`: a regression is a
case whose expected findings stop being produced, or a clean case that starts producing findings.
