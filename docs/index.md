# [Project Name] — Context Index

> Always pass this file to Claude. Then add the specific files for your current task.

---

## What this project is about
→ `context/project.md`
Stack, goals, technical constraints, coding conventions.

## Who works on it and how
→ `context/team.md`
Roles, branch strategy, review process.

## Architecture decisions (ADR)
→ `context/decisions.md`
Why we chose X over Y. Read this before proposing alternatives.

---

## Current task

| Task type | Files to include |
|---|---|
| New issue / feature | `specs/issue-XXX.md` |
| Planning session | `planning/instructions.md` + active milestone |
| UI work | `ui/components.md` + optional `[feature].md` |
| Architecture decision | `context/decisions.md` |
| Review / refactor | `context/project.md` + relevant spec files |

---

## Active milestone
→ `planning/milestone-01.md`
Open issues, priorities, dependencies.

---

## Rules for Claude

- Do not invent conventions that are not in `project.md`
- Before suggesting a new library, check that it does not conflict with `decisions.md`
- Issues in `specs/` are atomic: work on one at a time
- If a decision changes during work, flag it explicitly
