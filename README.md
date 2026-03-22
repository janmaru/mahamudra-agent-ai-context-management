# AI Context Management — A Strategy for Claude Code

**Date:** 2026-03-21
**Scope:** managing Claude Code's context window on multi-language projects, teams of 2–3 people

---

## Project structure

```
docs/
├── index.md                          # entry point for Claude — always include this
│
├── context/
│   ├── project.md                    # stack, goals, constraints, coding conventions
│   ├── team.md                       # roles, responsibilities, git workflow
│   └── decisions.md                  # ADR - Architecture Decision Records
│
├── planning/
│   ├── instructions.md               # how to run planning sessions with Claude
│   └── milestone-01.md               # current milestone
│
├── specs/
│   └── _template.md                  # reusable template for new issues
│
└── ui/
    └── components.md                 # design system, patterns, UI conventions
```

### How to use it

Always pass [`docs/index.md`](docs/index.md) to Claude, then add the files relevant to your current task:

| Task type | Files to include |
|---|---|
| New issue / feature | [`specs/issue-XXX.md`](docs/specs/_template.md) |
| Planning session | [`planning/instructions.md`](docs/planning/instructions.md) + [active milestone](docs/planning/milestone-01.md) |
| UI work | [`ui/components.md`](docs/ui/components.md) |
| Architecture decision | [`context/decisions.md`](docs/context/decisions.md) |
| Review / refactor | [`context/project.md`](docs/context/project.md) + relevant spec files |

---

## The problem

Claude Code's default setup (hierarchical `CLAUDE.md` files, global memory, hooks) degrades
performance on real projects. It accumulates contradictory or irrelevant instructions in the
context window. Files shared via git by other team members add uncontrolled noise.

## Core decision: manual, just-in-time context management

No automatic `CLAUDE.md` files, no hooks. Context is fed to Claude manually, session by session,
picking only the files relevant to the current task.

**Rationale:** full control over what enters the context window, no cross-project interference,
files are versioned and readable by the whole team.

**Accepted trade-off:** the developer must remember which files to pass. Mitigated by [`index.md`](docs/index.md).

## The docs/ folder as a manual RAG system

Context documents are organized into thematic folders with atomic granularity.
Each issue gets its own file. Each UI area gets its own file only when the context
is large enough to justify it.

**Rationale:** avoid monolithic files where signal drowns in noise. Load only what
the current task actually needs.

## Atomic issues with a standard template

Every issue/feature has its own [spec file](docs/specs/_template.md) with a goal, scope,
acceptance criteria, and notes for Claude. The template explicitly includes an "out of scope"
section and a "notes for Claude" section.

**Rationale:** atomic issues prevent Claude from dragging in context from unrelated features.

## Planning and implementation are separate

Planning sessions have [dedicated instructions](docs/planning/instructions.md) and follow
an explicit phased process (analysis → breakdown → review → spec → prioritization).
Claude does not write code during planning.

**Rationale:** mixing planning and implementation in the same session degrades the quality
of both. Explicit phase gates with human confirmation prevent scope creep.

## ADRs for architecture decisions

[Technical decisions](docs/context/decisions.md) are tracked with context, evaluated options,
and the reasoning behind the choice. Superseded decisions are not deleted — they are marked
as `superseded`.

**Rationale:** prevents Claude (and team members) from re-proposing alternatives that were
already evaluated and rejected.

---

## Claude's file hierarchy — what gets loaded and when

### Levels, from lowest to highest priority

```
~/.claude/CLAUDE.md              → user-global, always loaded, all projects
~/.claude/CLAUDE.local.md        → user-local, not in git
[project-root]/CLAUDE.md         → project-shared, in git, always loaded
[project-root]/CLAUDE.local.md   → project-local, not in git
[subdir]/CLAUDE.md               → subdirectory, loaded on-demand only
[project-root]/.claude/rules/*.md → modular rules, loaded at launch or by glob match
~/.claude/projects/[id]/MEMORY.md → auto memory, only first 200 lines per session
```

When files conflict, the one closest to the project (most specific) wins.

### Loaded automatically every session

- `~/.claude/CLAUDE.md` — always, no exceptions
- `CLAUDE.md` at project root — always
- `.claude/rules/*.md` without `paths:` frontmatter — always
- `MEMORY.md` auto memory — always, but **only the first 200 lines**

### Loaded on-demand (not at launch)

- `CLAUDE.md` in subdirectories — **only when Claude reads files in that directory**
- `.claude/rules/*.md` with `paths:` frontmatter — only when Claude touches files
  matching the specified glob pattern
- Auto memory topic files — on-demand, Claude reads them when needed

### Character limits and context window impact

| File | Recommended limit | What happens beyond the limit |
|---|---|---|
| `CLAUDE.md` (any level) | **max 200 lines** | instruction adherence degrades |
| `CLAUDE.md` sweet spot | 30–100 lines | best response accuracy |
| Effective tokens (50 lines) | ~2,000 tokens | < 1% of context window |
| Effective tokens (200 lines) | ~8,000 tokens | starts becoming noise |
| `MEMORY.md` auto memory | 200 lines hard limit | the rest is never loaded |

### Why we chose not to use these mechanisms

The manual `docs/` structure intentionally replaces nested `CLAUDE.md` files and
`.claude/rules/` because:

1. **No implicit loading** — we know exactly what is in context
2. **No loading bugs** — subdirectory `CLAUDE.md` behavior is documented but unreliable in practice
3. **Zero wasted tokens on irrelevant context** — working on a backend issue? Nothing from UI gets loaded
4. **Version-controlled and team-readable** — `docs/` files are part of the project, not hidden config in `.claude/`

---

## What was excluded and why

- **Hooks:** add complexity with no clear benefit for this workflow
- **Nested CLAUDE.md files:** the primary source of the observed degradation — removed entirely
- **Global auto memory:** too much cross-project noise — replaced by manual context
