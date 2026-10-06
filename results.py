"""Structured, backwards-compatible normalization results."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["NormalizationIssue", "NormalizationResult", "NormalizationAmbiguityError"]


@dataclass(frozen=True)
class NormalizationIssue:
    """An unresolved source span using zero-based Python character offsets."""

    start: int
    end: int
    category: str
    message: str


@dataclass(frozen=True)
class NormalizationResult:
    """The normalized text plus any expressions intentionally left unresolved."""

    text: str
    complete: bool
    issues: tuple[NormalizationIssue, ...] = ()


class NormalizationAmbiguityError(ValueError):
    """Raised when ``ambiguity_policy='reject'`` encounters an ambiguous span."""

    def __init__(self, issues: tuple[NormalizationIssue, ...]):
        super().__init__("Ambiguous expression(s): " + ", ".join(
            f"{issue.start}:{issue.end}" for issue in issues
        ))
        self.issues = issues
