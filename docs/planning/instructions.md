# Planning Instructions — How to work with Claude

> This file defines the planning process. Pass it along with the active milestone.
> Planning and implementation are **separate sessions**. Claude does not write code
> during planning.

---

## Core principle

Smart models perform worse with prescriptive step-by-step instructions.
Give Claude the **problem, constraints, and output shape** — not instructions
for how to think. The planning process below defines gates and deliverables,
not reasoning steps.

---

## When to enter plan mode

- Any task with 3+ steps or architectural decisions
- When something goes sideways: **stop and re-plan immediately** — don't keep pushing
- When you need verification steps, not just building
- When scope is ambiguous — write detailed specs upfront to reduce ambiguity

---

## Session setup

At the start of every planning session, always specify:

- **Session goal:** what we want to decide or produce today
- **Horizon:** this milestone / next sprint / long term
- **Constraints:** time, resources, blocking dependencies
- **Context files:** which `domain/` and `tech/` files Claude should read

---

## Planning process

### Phase 1 — Analysis

Claude reads the relevant context:
- `tech/project.md` + `tech/decisions.md` for technical constraints
- `domain/[area].md` for the functional area involved

Output: understanding of the problem space, identified risks, open questions.

**Gate: human confirms the analysis is correct before proceeding.**

### Phase 2 — Breakdown

Claude proposes a split into atomic issues. Each issue must be:
- Small enough to implement in a single session
- Independent or with explicit dependencies
- Verifiable — has clear acceptance criteria

Output: list of proposed issues with titles, scope, and dependencies.

**Gate: human approves or revises the breakdown.**

### Phase 3 — Spec

Claude generates `specs/issue-XXX.md` for each approved issue,
following the `specs/_template.md` format.

Give Claude the problem and constraints for each issue. Do not dictate
the implementation approach — let Claude propose it in the spec.

Output: one spec file per issue, ready for implementation.

**Gate: human reviews specs. Reject if scope is unclear or acceptance criteria are not verifiable.**

### Phase 4 — Prioritization

Together, define the order within the milestone:

```
P0 — blocker, nothing works without this
P1 — core to the milestone, must be done this cycle
P2 — useful but can be deferred to the next milestone
P3 — backlog, to be reassessed
```

Output: updated `planning/milestone-XX.md` with ordered issues.

---

## Subagent strategy during planning

Use subagents liberally to keep the main context window clean:

- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution
- Subagents report back results; the main agent synthesizes

When tasks are independent, run subagents in parallel.
When tasks depend on each other, run them sequentially.

---

## Verification and self-improvement

- Never mark a task complete without proving it works (tests, logs, diff)
- Ask yourself: "Would a staff engineer approve this?"
- If a fix feels hacky, pause — there's probably a more elegant way
- After any correction from the user, flag lessons that apply beyond this session
  so they can be saved to the relevant doc or memory

---

## Task management flow

1. **Plan** — write plan to `specs/` with checkable items
2. **Verify plan** — human checks in before implementation starts
3. **Track** — mark items complete as you go, summarize changes at each step
4. **Document** — update the relevant `domain/` file with what was built
5. **Capture lessons** — flag corrections that apply beyond this session

---

## Session outputs

- Issue specs following `specs/_template.md` format
- Dependency list between issues
- Flags on technical risks or ambiguities
- Updated `planning/milestone-XX.md` and `tech/decisions.md` if needed
- **No code** — analysis and structure only

---

## Anti-patterns

- Mixing planning and implementation in the same session
- Issues without verifiable acceptance criteria
- Expanding scope of an existing issue — open a new one instead
- Implicit dependencies: if A blocks B, write it down
- Prescriptive step-by-step reasoning instructions — give problem and constraints
- Pushing forward when something goes sideways — stop and re-plan
- Skipping verification — "it looks right" is not proof
