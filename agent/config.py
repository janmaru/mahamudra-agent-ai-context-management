"""
Configuration for the Trajectory Evaluator.

Adjust these settings based on your agent's use case:
- Interactive (human-in-the-loop): you probably don't need this at all
- Autonomous (multi-step, no human): use the evaluator on every step
- Long-running (hours/days): use evaluator + memory triplets + pruning
"""

# Evaluator model — should be small, fast, deterministic
EVALUATOR_MODEL = "claude-haiku-4-5-20251001"
EVALUATOR_TEMPERATURE = 0

# Self-correction loop
MAX_ATTEMPTS = 3  # retries before escalating to human review

# Memory
KEEP_LAST_TRIPLETS = 10  # how many recent triplets to keep after pruning
