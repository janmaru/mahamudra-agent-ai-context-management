# Planning Instructions — How to work with Claude

> This file defines the planning process. Pass it along with the active milestone.

---

## Session setup

At the start of every planning session, always specify:
- **Session goal:** what we want to decide or produce today
- **Horizon:** this milestone / next sprint / long term
- **Constraints:** time, resources, blocking dependencies

---

## Standard process for a new feature

1. **Analysis** — Claude reads `tech/project.md` + `tech/decisions.md`
2. **Breakdown** — Claude proposes a split into atomic issues
3. **Review** — we approve or revise the breakdown
4. **Spec** — Claude generates `specs/issue-XXX.md` for each approved issue
5. **Prioritization** — together we define the order within the milestone

Rule: do not move to the next phase without explicit confirmation.

---

## Priority levels

Always use this scheme when ordering issues in a milestone:

```
P0 — blocker, nothing works without this
P1 — core to the milestone, must be done this cycle
P2 — useful but can be deferred to the next milestone
P3 — backlog, to be reassessed
```

---

## Expected outputs from Claude during planning

- Issue breakdown following the `specs/_template.md` format
- Dependency list between issues (which unblocks which)
- Explicit flags on technical risks or ambiguities in the specs
- No implementation during planning — analysis and structure only

---

## Milestone updates

At the end of every planning session, Claude updates:
- `planning/milestone-XX.md` with issues added/modified/closed
- `tech/decisions.md` if new architecture decisions emerged

---

## Anti-patterns to avoid

- Do not mix planning and implementation in the same session
- Do not open issues without verifiable acceptance criteria
- Do not expand the scope of an existing issue — open a new one instead
- Do not leave implicit dependencies: if A blocks B, write it down explicitly
