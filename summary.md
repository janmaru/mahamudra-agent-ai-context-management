# Context Management — Summary delle scelte

**Data:** 2026-03-21  
**Contesto:** gestione del contesto per Claude Code su progetti multi-linguaggio, team 2-3 persone

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

**Trade-off accettato:** il developer deve ricordare quali file passare. Mitigato dall'`index.md`.

## Struttura docs/ come sistema RAG manuale

I documenti di contesto sono organizzati in cartelle tematiche (`context/`, `planning/`, `specs/`,
`ui/`) con granularità atomica. Ogni issue ha il proprio file. Ogni area UI ha il proprio file
solo se il contesto è abbastanza grande da giustificarlo.

**Motivazione:** evitare file monolitici dove il segnale si perde nel rumore. Caricare solo
quello che serve per il task corrente.

## index.md come punto di ingresso fisso

Un file indice che mappa tipo di task → file da passare. Non contiene contenuto, solo
riferimenti. Viene passato sempre, insieme ai file specifici del task.

**Motivazione:** elimina il problema del "cosa passo oggi" senza dover ricordare la struttura
a memoria.

## Issue atomici con template standardizzato

Ogni issue/feature ha uno spec proprio con obiettivo, scope, acceptance criteria e note per
Claude. Il template include esplicitamente un campo "out of scope" e "note per Claude".

**Motivazione:** issue atomici evitano che Claude porti contesto di feature non correlate.
Il campo "note per Claude" permette di gestire vincoli specifici senza inquinare il contesto
globale.

## Planning separato dall'implementazione

Le sessioni di planning hanno istruzioni dedicate e un processo esplicito a fasi (analisi →
breakdown → review → spec → priorità). Claude non implementa durante il planning.

**Motivazione:** mescolare planning e implementazione nella stessa sessione degrada la qualità
di entrambi. Il processo a fasi con conferme esplicite evita derive di scope.

## ADR per le decisioni architetturali

Le decisioni tecniche vengono tracciate con contesto, opzioni valutate e ragione della scelta.
Le decisioni superate non vengono cancellate ma marcate come `superseded`.

**Motivazione:** evitare che Claude (o i membri del team) ripropongano alternative già valutate
e scartate. Riduce discussioni ridondanti e mantiene memoria delle motivazioni nel tempo.

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
- `.claude/rules/*.md` senza frontmatter `paths:` — sempre, ricorsivamente nelle sottocartelle di rules/
- `MEMORY.md` auto memory — sempre, ma **solo le prime 200 righe**

### Cosa viene caricato on-demand (non a launch)

- `CLAUDE.md` nelle sottocartelle — **solo quando Claude legge file in quella directory**,
  non al lancio. Attenzione: questo comportamento ha un bug noto (issue #2571 su GitHub):
  in alcuni casi le sottocartelle non vengono caricate anche se la documentazione lo promette.
  Non fare affidamento su questo meccanismo per contesto critico.
- `.claude/rules/*.md` con frontmatter `paths:` — solo quando Claude tocca file che
  corrispondono al glob pattern specificato nell'header YAML del file.
- Topic files dell'auto memory (`debugging.md`, `patterns.md`, ecc.) — on-demand,
  Claude li legge quando serve, non a launch.

### Limiti di caratteri e impatto sulla context window

| File | Limite raccomandato | Comportamento oltre il limite |
|---|---|---|
| `CLAUDE.md` (qualsiasi livello) | **max 200 righe** | caricato comunque, ma l'aderenza alle istruzioni degrada |
| `CLAUDE.md` ottimale | 30–100 righe | massima precisione nelle risposte |
| Token effettivi (50 righe) | ~2.000 token | < 1% della context window |
| Token effettivi (200 righe) | ~8.000 token | inizia a essere rumore |
| `MEMORY.md` auto memory | 200 righe hard limit | il resto non viene caricato a session start |

**Regola pratica:** un `CLAUDE.md` di 200 righe consuma circa 8.000 token. Su una
context window da 200K token sembra poco, ma il problema non è la percentuale — è che
tutto viene iniettato su **ogni singolo messaggio** della sessione, non solo all'inizio.
Un file monolitico da 400 righe moltiplica il costo per ogni turno di conversazione.

### Perché abbiamo scelto di non usare questi meccanismi

La struttura `docs/` manuale sostituisce intenzionalmente `CLAUDE.md` annidati e
`.claude/rules/` perché:

1. **Nessun caricamento implicito** — sappiamo esattamente cosa è in context
2. **Nessun bug di loading** — il comportamento delle sottocartelle CLAUDE.md è
   documentato ma inaffidabile in pratica
3. **Zero token sprecati su contesto non rilevante** — se lavoro su un issue backend
   non carico nulla di UI
4. **Versionabile e leggibile dal team** — i file `docs/` sono parte del progetto,
   non configurazione nascosta in `.claude/`

L'unica eccezione accettabile sarebbe un `~/.claude/CLAUDE.md` globale minimalista
(< 30 righe) con preferenze stabili e universali: lingua di risposta, stile commit,
tool preferiti — cose che non cambiano mai tra progetti.

---

## Cosa è stato escluso e perché

- **Hook:** aggiungono complessità senza benefici chiari per questo workflow
- **CLAUDE.md annidati:** fonte principale del degrado osservato, rimossi completamente
- **Memory globale automatica:** troppo rumore cross-progetto, sostituita dal contesto manuale
