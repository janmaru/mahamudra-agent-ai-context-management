# [Nome Progetto] — Context Index

> Passa sempre questo file a Claude. Aggiungi i file specifici al task corrente.

---

## Cos'è questo progetto
→ `context/project.md`
Stack, obiettivo, vincoli tecnici, convenzioni di codice.

## Chi lavora e come
→ `context/team.md`
Ruoli, branch strategy, review process.

## Decisioni architetturali (ADR)
→ `context/decisions.md`
Perché abbiamo scelto X invece di Y. Da leggere prima di proporre alternative.

---

## Task corrente

| Tipo task | File da aggiungere |
|---|---|
| Nuovo issue / feature | `specs/issue-XXX.md` |
| Planning sessione | `planning/instructions.md` + milestone attiva |
| Lavoro su UI | `ui/components.md` + eventuale `[feature].md` |
| Decisione architetturale | `context/decisions.md` |
| Review / refactor | `context/project.md` + file specs dell'area |

---

## Milestone attiva
→ `planning/milestone-01.md`
Issue aperti, priorità, dipendenze.

---

## Regole per Claude

- Non inventare convenzioni non presenti in `project.md`
- Prima di proporre una libreria nuova, verifica che non contraddica `decisions.md`
- Gli issue in `specs/` sono atomici: lavora su uno alla volta
- Se una decisione cambia durante il lavoro, segnalalo esplicitamente
