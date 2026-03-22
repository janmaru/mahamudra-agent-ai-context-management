# [Project Name] — Context Index

> Always pass this file to Claude. Then add the specific files for your current task.

---

## Tech

Stack, constraints, conventions, decisions. Rarely changes.

| File | Content |
|---|---|
| `tech/project.md` | Stack, goals, technical constraints, coding conventions |
| `tech/team.md` | Roles, branch strategy, review process |
| `tech/decisions.md` | ADR — why we chose X over Y |
| `tech/trajectory-evaluator.md` | Verify-before-commit pattern for autonomous agents |

## Domain

Functional areas, split by bounded context. Each file covers one area.

| File | Content |
|---|---|
| `domain/[area].md` | Concepts, workflows, business rules, current state |

## Specs

One file per user story / issue. Not pushed to git — local working docs.

| File | Content |
|---|---|
| `specs/issue-XXX.md` | Goal, scope, acceptance criteria, notes for Claude |

## Planning

Planning sessions and milestones. Not pushed to git.

| File | Content |
|---|---|
| `planning/instructions.md` | How to run planning sessions with Claude |
| `planning/milestone-XX.md` | Current milestone, priorities, dependencies |

---

## What to pass to Claude

| Task type | Files to include |
|---|---|
| New issue / feature | this index + `specs/issue-XXX.md` + relevant `domain/` file(s) |
| Planning session | this index + `planning/instructions.md` + active milestone |
| Domain exploration | this index + relevant `domain/` file(s) |
| Architecture decision | this index + `tech/decisions.md` |
| Review / refactor | this index + `tech/project.md` + relevant spec and domain files |

---

## Rules for Claude

- Do not invent conventions that are not in `tech/project.md`
- Before suggesting a new library, check that it does not conflict with `tech/decisions.md`
- Issues in `specs/` are atomic: work on one at a time
- If a decision changes during work, flag it explicitly
- Domain files describe what has been built — keep them up to date after significant changes
