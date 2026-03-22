# Trajectory Evaluator — Verify-Before-Commit Pattern

> Programmatic solution to error propagation, state drift, and knowledge conflict
> in agentic AI. Complements the manual context strategy described in the README.

---

## The problem it solves

The manual `docs/` strategy controls **what enters** the context window.
The Trajectory Evaluator controls **what gets accepted as valid state** during
agent execution. Together they cover both sides: input quality and output integrity.

Without verification, an agent that hallucinates at step *k* saves that hallucination
to memory, and every subsequent step builds on a false foundation.

---

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│    Agent     │────→│   Environment   │────→│  Evaluator   │
│  (propose)   │     │   (execute)     │     │  (verify)    │
└─────────────┘     └─────────────────┘     └──────┬──────┘
       ↑                                           │
       │            ┌─────────────────┐            │
       └────────────│     Memory      │←───────────┘
        re-prompt   │  (commit/reject)│   commit only if valid
        on failure  └─────────────────┘
```

The Evaluator is a **middleware layer** between the agent's reasoning engine and
its memory storage. Nothing reaches long-term memory without passing verification.

---

## Core implementation

### The self-correction loop

Step *k+1* never starts until step *k* is verified. Max 3 attempts before escalating.

```python
def run_agent_step(agent, memory, evaluator, task):
    """
    Execute a single agent step with trajectory verification.
    Returns True if the step was verified, False if all attempts failed.
    """
    verified = False
    attempts = 0

    while not verified and attempts < 3:
        # Step k: agent generates thought + action
        proposal = agent.think(task, memory.get_context())
        observation = agent.execute(proposal.action)

        # Evaluator acts as gatekeeper
        is_valid, critique = evaluator.verify(proposal, observation)

        if is_valid:
            # A posteriori justification met — commit to long-term memory
            memory.commit(proposal, observation)
            verified = True
        else:
            # Conflict detected — force the agent to reconcile
            task = (
                f"Your last action failed validation: {critique}. "
                f"Re-evaluate your approach."
            )
            attempts += 1

    return verified
```

### The contextual fidelity check

Addresses the *a priori* bias problem: when the model's weights contradict
the retrieved context.

```python
FIDELITY_PROMPT = """
You are a factual consistency checker.

Retrieved context: {retrieved_context}
Agent claim: {agent_claim}

Rules:
- If the claim contradicts the retrieved context, respond: FIDELITY_FAILURE
- If the claim is consistent, respond: PASS
- If the retrieved context is ambiguous, respond: AMBIGUOUS

Do not explain. Respond with one word only.
"""

def check_fidelity(evaluator_llm, retrieved_context, agent_claim):
    """
    Use a small, high-precision model to detect when the agent's
    pre-trained knowledge overrides the provided context.
    """
    result = evaluator_llm.invoke(
        FIDELITY_PROMPT.format(
            retrieved_context=retrieved_context,
            agent_claim=agent_claim,
        )
    )
    return result.strip()
```

Use a small, deterministic model (e.g. Haiku with temperature 0) for the evaluator.
The evaluator must be cheaper and faster than the agent — it runs on every step.

### Memory triplets

Instead of flat summaries, store memory as structured triplets that preserve
failure context through compression.

```python
from dataclasses import dataclass
from enum import Enum

class ValidationStatus(Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    AMBIGUOUS = "ambiguous"

@dataclass
class MemoryTriplet:
    action: str          # what the agent did
    result: str          # what actually happened
    status: ValidationStatus  # evaluator verdict

class VerifiableMemory:
    """
    Memory store that keeps triplets instead of flat text.
    On pruning, verified actions can be summarized but failed
    actions are always preserved in full.
    """

    def __init__(self):
        self.triplets: list[MemoryTriplet] = []

    def commit(self, proposal, observation, status=ValidationStatus.VERIFIED):
        self.triplets.append(
            MemoryTriplet(
                action=str(proposal),
                result=str(observation),
                status=status,
            )
        )

    def get_context(self, max_tokens: int = 4000) -> str:
        """
        Build context for the agent. Failed triplets are never pruned —
        they prevent the agent from repeating the same mistake.
        """
        locked = [t for t in self.triplets if t.status == ValidationStatus.FAILED]
        unlocked = [t for t in self.triplets if t.status != ValidationStatus.FAILED]

        context_parts = []

        # Failed attempts always included — these are self-correction triggers
        for t in locked:
            context_parts.append(
                f"[FAILED] Action: {t.action} | Result: {t.result}"
            )

        # Verified actions included newest-first, pruned if over budget
        for t in reversed(unlocked):
            entry = f"[OK] Action: {t.action} | Result: {t.result}"
            context_parts.append(entry)

        return "\n".join(context_parts)

    def prune(self):
        """
        Selective pruning: remove old verified triplets but lock
        all failed ones. This prevents the agent from losing the
        reasons why a path was abandoned.
        """
        self.triplets = [
            t for t in self.triplets
            if t.status == ValidationStatus.FAILED
        ] + self.triplets[-10:]  # keep last 10 regardless of status
```

---

## Operational integration

### Where this fits in a project

```
your-project/
├── docs/                     # manual context strategy (this repo)
│   ├── index.md
│   ├── domain/
│   └── tech/
├── agent/                    # trajectory evaluator runtime
│   ├── evaluator.py          # core loop + fidelity check
│   ├── memory.py             # VerifiableMemory + triplets
│   └── config.py             # model settings, thresholds
└── ...
```

The `docs/` folder feeds **what the agent knows**. The `agent/` folder controls
**how the agent validates what it does**.

### How to use it

1. **Wrap your agent loop** — replace direct memory writes with `run_agent_step()`
2. **Configure the evaluator model** — use a small, fast model (Haiku, GPT-4o-mini)
   with temperature 0 for deterministic checks
3. **Set attempt limits** — 3 is a reasonable default; after 3 failures, escalate
   to human review instead of looping
4. **Monitor fidelity failures** — log them. A high rate of `FIDELITY_FAILURE` means
   your retrieved context is too sparse or ambiguous — improve the domain files

### When to use it vs. when manual context is enough

| Scenario | Approach |
|---|---|
| Human-in-the-loop with Claude Code | Manual context strategy (`docs/`) is sufficient |
| Autonomous agent running multi-step tasks | Trajectory Evaluator required |
| Agent with long-running memory (hours/days) | Trajectory Evaluator + memory triplets |
| One-shot prompt with RAG | Fidelity check alone may be enough |

### Adapting to frameworks

The pattern is framework-agnostic. To integrate with common stacks:

- **LangChain**: implement as a custom `CallbackHandler` that intercepts `on_agent_action`
- **AutoGPT**: replace the memory commit step in the main loop
- **Custom stack**: wrap the agent's `step()` method as shown above

---

## Limits of this approach

- The evaluator itself is an LLM — it can also hallucinate. Mitigated by using
  a smaller model with constrained output (single-word responses)
- Adds latency: every step requires an extra LLM call. Acceptable for autonomous
  agents, unnecessary for interactive human-in-the-loop sessions
- The 3-attempt limit is a heuristic. Some failures need human intervention,
  not more retries
