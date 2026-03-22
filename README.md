# AI Context Management — Strategia per Claude Code

**Data:** 2026-03-21
**Contesto:** gestione del contesto per Claude Code su progetti multi-linguaggio, team 2-3 persone

---

## Struttura del progetto

```
docs/
├── index.md                          # punto di ingresso per Claude, sempre da passare
│
├── context/
│   ├── project.md                    # stack, obiettivo, vincoli, convenzioni globali
│   ├── team.md                       # chi fa cosa, responsabilità, workflow git
│   └── decisions.md                  # ADR - Architecture Decision Records
│
├── planning/
│   ├── instructions.md               # come fare planning con Claude
│   └── milestone-01.md               # milestone attiva
│
├── specs/
│   └── _template.md                  # template riutilizzabile per nuovi issue
│
└── ui/
    └── components.md                 # design system, pattern, convenzioni UI
```

### Come usarlo

Passa sempre [`docs/index.md`](docs/index.md) a Claude, poi aggiungi i file specifici al task:

| Tipo task | File da aggiungere |
|---|---|
| Nuovo issue / feature | [`specs/issue-XXX.md`](docs/specs/_template.md) |
| Planning sessione | [`planning/instructions.md`](docs/planning/instructions.md) + [milestone attiva](docs/planning/milestone-01.md) |
| Lavoro su UI | [`ui/components.md`](docs/ui/components.md) |
| Decisione architetturale | [`context/decisions.md`](docs/context/decisions.md) |
| Review / refactor | [`context/project.md`](docs/context/project.md) + file specs dell'area |

---

## Problema di partenza

La struttura standard di Claude Code (file `CLAUDE.md` gerarchici, memory globale, hook) degrada
le performance su progetti specifici perché accumula istruzioni contraddittorie o irrilevanti nel
contesto. I file condivisi via git da altri membri del team aggiungono rumore non controllato.

## Scelta principale: context management manuale (just-in-time)

Niente `CLAUDE.md` automatici, niente hook. Il contesto viene passato manualmente a Claude
sessione per sessione, scegliendo solo i file rilevanti al task corrente.

**Motivazione:** controllo totale su cosa entra nel contesto, nessuna interferenza tra progetti,
file versionati e leggibili da tutti i membri del team.

**Trade-off accettato:** il developer deve ricordare quali file passare. Mitigato dall'[`index.md`](docs/index.md).

## Struttura docs/ come sistema RAG manuale

I documenti di contesto sono organizzati in cartelle tematiche con granularità atomica.
Ogni issue ha il proprio file. Ogni area UI ha il proprio file solo se il contesto è
abbastanza grande da giustificarlo.

**Motivazione:** evitare file monolitici dove il segnale si perde nel rumore. Caricare solo
quello che serve per il task corrente.

## Issue atomici con template standardizzato

Ogni issue/feature ha uno [spec proprio](docs/specs/_template.md) con obiettivo, scope,
acceptance criteria e note per Claude. Il template include esplicitamente un campo
"out of scope" e "note per Claude".

**Motivazione:** issue atomici evitano che Claude porti contesto di feature non correlate.

## Planning separato dall'implementazione

Le sessioni di planning hanno [istruzioni dedicate](docs/planning/instructions.md) e un
processo esplicito a fasi (analisi → breakdown → review → spec → priorità).
Claude non implementa durante il planning.

**Motivazione:** mescolare planning e implementazione nella stessa sessione degrada la qualità
di entrambi. Il processo a fasi con conferme esplicite evita derive di scope.

## ADR per le decisioni architetturali

Le [decisioni tecniche](docs/context/decisions.md) vengono tracciate con contesto, opzioni
valutate e ragione della scelta. Le decisioni superate non vengono cancellate ma marcate
come `superseded`.

**Motivazione:** evitare che Claude (o i membri del team) ripropongano alternative già valutate
e scartate.

---

## Gerarchia dei file Claude — cosa viene letto e quando

### I livelli, in ordine di priorità crescente

```
~/.claude/CLAUDE.md              → globale utente, sempre caricato, tutti i progetti
~/.claude/CLAUDE.local.md        → globale locale, non in git
[project-root]/CLAUDE.md         → progetto condiviso, in git, sempre caricato
[project-root]/CLAUDE.local.md   → progetto locale, non in git
[subdir]/CLAUDE.md               → sottocartella, caricato solo on-demand
[project-root]/.claude/rules/*.md → regole modulari, caricate a launch o per glob
~/.claude/projects/[id]/MEMORY.md → auto memory, solo prime 200 righe a ogni sessione
```

In caso di conflitto tra livelli, vince il file più vicino al progetto (più specifico).

### Cosa viene caricato automaticamente a ogni sessione

- `~/.claude/CLAUDE.md` — sempre, senza eccezioni
- `CLAUDE.md` nella root del progetto — sempre
- `.claude/rules/*.md` senza frontmatter `paths:` — sempre
- `MEMORY.md` auto memory — sempre, ma **solo le prime 200 righe**

### Cosa viene caricato on-demand (non a launch)

- `CLAUDE.md` nelle sottocartelle — **solo quando Claude legge file in quella directory**
- `.claude/rules/*.md` con frontmatter `paths:` — solo quando Claude tocca file che
  corrispondono al glob pattern specificato
- Topic files dell'auto memory — on-demand, Claude li legge quando serve

### Limiti di caratteri e impatto sulla context window

| File | Limite raccomandato | Comportamento oltre il limite |
|---|---|---|
| `CLAUDE.md` (qualsiasi livello) | **max 200 righe** | l'aderenza alle istruzioni degrada |
| `CLAUDE.md` ottimale | 30–100 righe | massima precisione nelle risposte |
| Token effettivi (50 righe) | ~2.000 token | < 1% della context window |
| Token effettivi (200 righe) | ~8.000 token | inizia a essere rumore |
| `MEMORY.md` auto memory | 200 righe hard limit | il resto non viene caricato |

### Perché abbiamo scelto di non usare questi meccanismi

La struttura `docs/` manuale sostituisce intenzionalmente `CLAUDE.md` annidati e
`.claude/rules/` perché:

1. **Nessun caricamento implicito** — sappiamo esattamente cosa è in context
2. **Nessun bug di loading** — il comportamento delle sottocartelle CLAUDE.md è inaffidabile
3. **Zero token sprecati su contesto non rilevante** — carico solo quello che serve
4. **Versionabile e leggibile dal team** — i file `docs/` sono parte del progetto

---

## Cosa è stato escluso e perché

- **Hook:** aggiungono complessità senza benefici chiari per questo workflow
- **CLAUDE.md annidati:** fonte principale del degrado osservato, rimossi completamente
- **Memory globale automatica:** troppo rumore cross-progetto, sostituita dal contesto manuale
