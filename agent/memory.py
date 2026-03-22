"""
Verifiable memory with triplet storage.

Instead of flat text summaries, stores (Action, Result, Validation_Status).
Failed triplets are never pruned — they act as self-correction triggers
that survive context compression.
"""

from dataclasses import dataclass, field
from enum import Enum


class ValidationStatus(Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    AMBIGUOUS = "ambiguous"


@dataclass
class MemoryTriplet:
    action: str
    result: str
    status: ValidationStatus


class VerifiableMemory:
    """
    Memory store that keeps triplets instead of flat text.
    On pruning, verified actions can be summarized but failed
    actions are always preserved in full.
    """

    def __init__(self, keep_last: int = 10):
        self.triplets: list[MemoryTriplet] = []
        self._keep_last = keep_last

    def commit(self, action: str, result: str, status: ValidationStatus = ValidationStatus.VERIFIED):
        self.triplets.append(
            MemoryTriplet(action=action, result=result, status=status)
        )

    def get_context(self) -> str:
        """
        Build context for the agent. Failed triplets are never pruned —
        they prevent the agent from repeating the same mistake.
        """
        parts: list[str] = []

        # Failed attempts always included first
        for t in self.triplets:
            if t.status == ValidationStatus.FAILED:
                parts.append(f"[FAILED] Action: {t.action} | Result: {t.result}")

        # Verified/ambiguous actions, newest first
        non_failed = [t for t in self.triplets if t.status != ValidationStatus.FAILED]
        for t in reversed(non_failed):
            tag = "OK" if t.status == ValidationStatus.VERIFIED else "AMBIGUOUS"
            parts.append(f"[{tag}] Action: {t.action} | Result: {t.result}")

        return "\n".join(parts)

    def prune(self):
        """
        Selective pruning: keep all failed triplets (self-correction triggers)
        plus the most recent N triplets regardless of status.
        """
        failed = [t for t in self.triplets if t.status == ValidationStatus.FAILED]
        recent = self.triplets[-self._keep_last:]

        # Merge without duplicates, preserving order
        seen = set()
        merged: list[MemoryTriplet] = []
        for t in failed + recent:
            key = id(t)
            if key not in seen:
                seen.add(key)
                merged.append(t)

        self.triplets = merged
