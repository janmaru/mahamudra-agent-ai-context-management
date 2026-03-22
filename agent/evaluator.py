"""
Trajectory Evaluator — verify-before-commit middleware.

Routes every agent action through a verification loop before
allowing it to be committed to long-term memory.
"""

from dataclasses import dataclass
from memory import VerifiableMemory, ValidationStatus


FIDELITY_PROMPT = """You are a factual consistency checker.

Retrieved context:
{retrieved_context}

Agent claim:
{agent_claim}

Rules:
- If the claim contradicts the retrieved context, respond: FIDELITY_FAILURE
- If the claim is consistent, respond: PASS
- If the retrieved context is ambiguous, respond: AMBIGUOUS

Do not explain. Respond with one word only."""


@dataclass
class Proposal:
    thought: str
    action: str


@dataclass
class EvalResult:
    is_valid: bool
    critique: str


class TrajectoryEvaluator:
    """
    Evaluates agent proposals against observations.
    Uses a small, fast model (e.g. Haiku) with temperature 0.
    """

    def __init__(self, evaluator_llm):
        """
        Args:
            evaluator_llm: any callable that takes a string prompt
                           and returns a string response.
                           E.g. a LangChain LLM, an Anthropic client wrapper,
                           or a simple function.
        """
        self._llm = evaluator_llm

    def verify(self, proposal: Proposal, observation: str) -> EvalResult:
        """
        Compare the agent's proposal against the actual observation.
        Returns whether the step is valid and a critique if not.
        """
        prompt = (
            f"The agent proposed: {proposal.thought}\n"
            f"The agent executed: {proposal.action}\n"
            f"The actual observation was: {observation}\n\n"
            f"Does the observation confirm the agent's proposal succeeded? "
            f"Respond PASS if yes, FAIL:<reason> if no."
        )
        response = self._llm(prompt).strip()

        if response.startswith("PASS"):
            return EvalResult(is_valid=True, critique="")

        reason = response.replace("FAIL:", "").strip() if ":" in response else response
        return EvalResult(is_valid=False, critique=reason)

    def check_fidelity(self, retrieved_context: str, agent_claim: str) -> str:
        """
        Detect when the agent's pre-trained knowledge overrides
        the provided context.

        Returns: "PASS", "FIDELITY_FAILURE", or "AMBIGUOUS"
        """
        prompt = FIDELITY_PROMPT.format(
            retrieved_context=retrieved_context,
            agent_claim=agent_claim,
        )
        return self._llm(prompt).strip()


def run_agent_step(agent, memory: VerifiableMemory, evaluator: TrajectoryEvaluator, task: str, max_attempts: int = 3) -> bool:
    """
    Execute a single agent step with trajectory verification.

    The agent proposes and executes an action. The evaluator checks the result.
    Only verified results are committed to memory. On failure, the agent is
    re-prompted with the critique. After max_attempts, returns False to
    signal that human intervention is needed.

    Args:
        agent: object with .think(task, context) -> Proposal
               and .execute(action) -> str
        memory: VerifiableMemory instance
        evaluator: TrajectoryEvaluator instance
        task: the current task description
        max_attempts: max retries before escalating (default 3)

    Returns:
        True if the step was verified, False if all attempts failed.
    """
    for attempt in range(max_attempts):
        proposal = agent.think(task, memory.get_context())
        observation = agent.execute(proposal.action)

        result = evaluator.verify(proposal, observation)

        if result.is_valid:
            memory.commit(
                action=proposal.action,
                result=observation,
                status=ValidationStatus.VERIFIED,
            )
            return True

        # Log the failure to memory so the agent won't repeat it
        memory.commit(
            action=proposal.action,
            result=f"REJECTED: {result.critique}",
            status=ValidationStatus.FAILED,
        )

        task = (
            f"Your last action failed validation: {result.critique}. "
            f"Re-evaluate your approach."
        )

    return False
