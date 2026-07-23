# Doc Sync — keep the docs true after implementing

> Used by the `implementer` skill (step 5), once the suite is green. Docs that describe behavior the
> code no longer has are worse than no docs: the next session trusts them.
>
> **Audit, don't recall.** "I don't think any doc mentions this" is not a check. Grep is.

## The doc set (all of it, every time)
| File | Describes |
|------|-----------|
| `CLAUDE.md` | Canonical project-wide rules/gotchas ("Always Remember"), architecture, run/test |
| `.github/copilot-instructions.md` | Mirror of `CLAUDE.md` + the **Stack** section (canonical home of dependency versions) |
| `README.md` | User-facing setup, run, config tables, project structure (Spanish) |
| `.claude/skills/references/project-architecture.md` | Module map, layering, responsibilities, invariants |
| `.claude/skills/references/project-tree.md` | Directory tree, per-file one-liners |
| `.claude/skills/references/common-commands.md` | Env / configure / run / test / lint / bump commands |
| `.claude/skills/references/common-workflows.md` | Recipes (YAML key / secret / assignment rule / email template / CLI flag / version bump) |
| `.claude/skills/planner/references/*`, `.claude/skills/implementer/references/*`, `.claude/skills/pr-review/references/*` | Planning / execution / review mechanics |
| `config/settings.example.yaml`, `.env.example` | Config templates — must list every key the code reads |
| `CHANGELOG.md` | Released changes (Keep a Changelog) |

## Procedure
1. **List what actually changed**: every module/function added, renamed or deleted; every behavior
   whose description would now be wrong; every dependency version; every command; every config key;
   every new gotcha.
2. **Grep the doc set for each item** — one `Grep` over `**/*.md` with the symbols alternated
   (`generate_assignments|PairValidator|settings.yaml|…`). Search the **behavior words** too, not
   just identifiers: a doc can describe a behavior without naming the function.
3. **Fix every hit** that the change made false. Moving `.env` → also fix every path in the README and
   the commands file. Renaming an entry point → fix every `python main.py` occurrence.
4. **Config keys are docs too**: a new key the code reads must appear in `config/settings.example.yaml`
   (or `.env.example`) and in the README's config section. A removed key must disappear from both.
5. **New reusable gotcha?** It belongs in `CLAUDE.md` "Always Remember" (canonical), with at most a
   one-line echo in the copilot mirror. A recipe-specific one goes in `common-workflows.md`.
6. **Single source of truth**: edit the canonical doc; don't restate the same fact in several files.
   Dependency versions live in the copilot **Stack** section only.
7. **Report a table**: every doc in the set, marked `updated (what)` or `checked — unaffected`. Never
   claim "docs are in sync" without having listed them.

## Pitfalls seen in practice
- Adding a YAML key to `config/settings.yaml` (gitignored, local only) and forgetting
  `settings.example.yaml` — the next clone of the repo breaks.
- Bumping the version in `pyproject.toml` while the README still shows the old one.
- Splitting or moving a module and leaving `project-architecture.md` describing the old layout.
- Leaving a "pending migration" warning block in a reference file after the migration landed.
- Pasting a real participant's name into a doc example instead of a fake one.
