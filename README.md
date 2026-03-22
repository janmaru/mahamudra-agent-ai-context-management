# AI Context Management — A Strategy for Claude Code

A strategy for managing Claude Code's context window on real projects.

---

## Project structure

```
docs/
├── index.md                          # entry point for Claude — always include this
│
├── tech/
│   ├── project.md                    # stack, goals, constraints, coding conventions
│   ├── team.md                       # roles, responsibilities, git workflow
│   └── decisions.md                  # ADR - Architecture Decision Records
│
├── domain/
│   ├── _template.md                  # reusable template for new domain areas
│   ├── [area-1].md                   # e.g. orders, authentication, billing
│   ├── [area-2].md                   # one file per bounded context / functional area
│   └── ...
│
├── planning/                         # local only — not pushed to git
│   ├── instructions.md               # how to run planning sessions with Claude
│   └── milestone-XX.md               # current milestone
│
├── specs/                            # local only — not pushed to git
│   ├── _template.md                  # reusable template for new issues
│   └── issue-XXX.md                  # one file per user story / issue
│
└── ui/
    └── components.md                 # design system, patterns, UI conventions
```

### How to use it

Always pass [`docs/index.md`](docs/index.md) to Claude, then add the files relevant to your current task:

| Task type | Files to include |
|---|---|
| New issue / feature | [`specs/issue-XXX.md`](docs/specs/_template.md) + relevant `domain/` file(s) |
| Planning session | [`planning/instructions.md`](docs/planning/instructions.md) + active milestone |
| Domain exploration | relevant `domain/` file(s) |
| UI work | [`ui/components.md`](docs/ui/components.md) + relevant `domain/` file(s) |
| Architecture decision | [`tech/decisions.md`](docs/tech/decisions.md) |
| Review / refactor | [`tech/project.md`](docs/tech/project.md) + relevant spec and domain files |

---

## Why this approach — the underlying problem

### Knowledge conflict in agentic AI

Any context provided to an LLM at inference time (*a posteriori*) competes with the
knowledge baked into its weights during training (*a priori*). Even when you supply
the correct facts via RAG, the model's internal weights — trained on billions of
parameters — act as a self-reinforcing bias. If a model has seen a "fact" 10,000 times
during training, a single retrieved document stating the opposite may be treated as noise.

When retrieved data is sparse or slightly ambiguous, the model fills in the blanks with
pre-trained knowledge, producing **hybrid responses** that look authoritative but are
factually groundless.

### Error propagation and state drift

In long-running agentic operations, a small logic error at step *k* gets saved to memory
and referenced at step *k+n* as ground truth. This creates two failure modes:

- **Error propagation** — a single hallucination becomes a "fact" in the agent's long-term memory
- **State drift** — the saved state diverges further from the actual goal with each operation

The outcome is **recursive failure**: the agent attempts to fix an error using the same
flawed logic that created it, leading to a loop.

### Context compression as information loss

When the context window fills up, the agent summarizes past states to save space.
Critical information — self-correction triggers, edge cases, constraints — gets flattened
out. The agent then operates on a lossy version of its own history, missing the details
that would have prevented mistakes.

### How this strategy mitigates these problems

| Problem | Mitigation |
|---|---|
| **Knowledge conflict** | Atomic, manual context: less noise = fewer chances for the model to prefer its weights over the provided context |
| **Hybrid responses** | Domain files explicitly describe what was built and how it works, reducing the ambiguity the model would fill with pre-trained knowledge |
| **Error propagation** | No auto-memory, no persistent state between sessions. Every session starts from versioned, human-verified files |
| **State drift** | Domain files are updated *after* completion, not during. The spec describes the goal, the domain file records the result — the delta is visible |
| **Recursive failure** | Planning and implementation are separated with explicit human gates. The agent does not self-correct — the developer intervenes between phases |
| **Context compression** | Just-in-time loading: only what the current task needs enters the window. A typical session (index + domain file + spec) stays under ~300 lines — compression never triggers |

The last point is key: context compression is a downstream problem caused by loading too
much upstream. This strategy acts upstream.

### Programmatic solution: Trajectory Evaluator

The manual `docs/` strategy controls what **enters** the context. For autonomous agents
that run without a human in the loop, you also need to control what gets **accepted as
valid state**. The Trajectory Evaluator pattern adds a verify-before-commit middleware:

1. The agent proposes an action and executes it
2. An evaluator compares the observation against the agent's internal state
3. Only verified results are committed to long-term memory
4. Failures are preserved as **memory triplets** `(Action, Result, Validation_Status)`
   that survive context pruning — preventing the agent from repeating the same mistake

For the full implementation with Python code, operational integration guide, and
framework-specific adapters, see [`docs/tech/trajectory-evaluator.md`](docs/tech/trajectory-evaluator.md).

For ongoing research on **verifiable memory** as a more general solution, see
[Verifiable Memory for LLM Agents](https://arxiv.org/abs/2504.07089).

---

### The practical problem

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
Each issue gets its own file. Each domain area gets its own file only when the context
is large enough to justify it.

**Rationale:** avoid monolithic files where signal drowns in noise. Load only what
the current task actually needs.

## Domain files — functional knowledge by area

The `domain/` folder is the living functional documentation of the project. Each file
covers one bounded context or functional area: its concepts, workflows, business rules,
and current state.

**How to split:** one file per area that has its own vocabulary, workflows, and rules.
If two areas share most of their concepts, keep them together. If a file grows beyond
~200 lines, look for a natural split.

**What goes in:** what has been built and how it works at the domain level — not code
structure, not technical details. Think of it as the knowledge a new team member needs
to understand a feature without reading the code.

**When to update:** after completing a user story that changes or adds domain behavior.
The spec file describes what to build; the domain file gets updated with what was built.

### Example: a project with three functional areas

```
domain/
├── _template.md
├── orders.md            # order lifecycle, statuses, cancellation rules
├── inventory.md         # stock levels, reservations, restock workflows
└── shipping.md          # carrier selection, tracking, delivery confirmation
```

A developer working on a shipping bug passes `index.md` + `domain/shipping.md`.
Claude gets the full shipping context without loading anything about orders or inventory.

A user story that spans two areas (e.g. "when an order is cancelled, release inventory")
gets both files: `domain/orders.md` + `domain/inventory.md`.

**Rationale:** a monolithic functional analysis file forces Claude to receive the entire
domain on every session. Splitting by area gives the same just-in-time control that
`specs/` gives for issues.

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

[Technical decisions](docs/tech/decisions.md) are tracked with context, evaluated options,
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
