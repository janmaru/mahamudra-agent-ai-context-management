# Istruzioni Planning — Come lavorare con Claude

> Questo file definisce il processo di planning. Passalo insieme alla milestone attiva.

---

## Modalità di sessione

Quando iniziamo una sessione di planning, specifica sempre:
- **Obiettivo sessione:** cosa vogliamo decidere o produrre oggi
- **Orizzonte:** questa milestone / prossimo sprint / lungo termine
- **Vincoli:** tempo, risorse, dipendenze bloccanti

---

## Processo standard per una nuova feature

1. **Analisi** — Claude legge `context/project.md` + `context/decisions.md`
2. **Breakdown** — Claude propone la suddivisione in issue atomici
3. **Review** — noi approviamo / modifichiamo il breakdown
4. **Spec** — Claude genera `specs/issue-XXX.md` per ogni issue approvato
5. **Priorità** — insieme definiamo l'ordine nella milestone

Regola: non passare alla fase successiva senza conferma esplicita.

---

## Come gestire le priorità

Usa sempre questo schema quando ordini gli issue in milestone:

```
P0 — bloccante, niente funziona senza questo
P1 — core della milestone, va fatto in questo ciclo
P2 — utile ma posticipabile alla milestone successiva
P3 — backlog, da rivalutare
```

---

## Output attesi da Claude durante il planning

- Breakdown issue in formato `specs/_template.md`
- Lista dipendenze tra issue (quale sblocca quale)
- Flag espliciti su rischi tecnici o ambiguità nelle specs
- Nessuna implementazione durante il planning — solo analisi e struttura

---

## Aggiornamento milestone

Al termine di ogni sessione di planning, Claude aggiorna:
- `planning/milestone-XX.md` con issue aggiunti/modificati/chiusi
- `context/decisions.md` se sono emerse nuove decisioni architetturali

---

## Anti-pattern da evitare

- Non fare planning e implementazione nella stessa sessione
- Non aprire issue senza acceptance criteria verificabili
- Non aggiungere scope a un issue esistente — aprirne uno nuovo
- Non lasciare dipendenze implicite: se A blocca B, scriverlo esplicitamente
