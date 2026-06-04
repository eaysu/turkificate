"""Core abstractions: the Normalizer interface (Strategy) and the Registry.

Every normalization concept is an independent subclass of ``Normalizer``. Classes
register themselves into a central registry via ``@register``, so that
``TurkishNormalizer`` can select and order concepts by name only
(e.g. "numbers", "dates").

Design principle: each normalizer does all of its setup (regex compilation, etc.)
in its constructor, while ``apply`` stays completely pure and side-effect free.
That lets a single instance be reused across thousands of texts.
"""

from abc import ABC, abstractmethod

__all__ = ["Normalizer", "register", "get_registry", "available_features"]

_REGISTRY: dict[str, type["Normalizer"]] = {}


class Normalizer(ABC):
    """Abstract base for a single normalization concept (Strategy)."""

    #: Unique name used in the registry and in feature selection.
    name: str = ""

    def __init__(self, **options):
        self.options = options
        self.configure(**options)

    def configure(self, **options) -> None:
        """Subclasses do their setup (e.g. regex compilation) here."""

    @abstractmethod
    def apply(self, text: str) -> str:
        """Transform the text and return the new text. Must be side-effect free."""

    def __call__(self, text: str) -> str:
        return self.apply(text)

    def __repr__(self) -> str:
        return f"<Normalizer {self.name!r}>"


def register(cls: type[Normalizer]) -> type[Normalizer]:
    """Decorator that registers a Normalizer subclass by its ``name`` attribute."""
    if not getattr(cls, "name", ""):
        raise ValueError(f"{cls.__name__} must define a 'name'.")
    if cls.name in _REGISTRY:
        raise ValueError(f"The name '{cls.name}' is already registered.")
    _REGISTRY[cls.name] = cls
    return cls


def get_registry() -> dict[str, type[Normalizer]]:
    """Return a copy of all registered normalizer classes."""
    return dict(_REGISTRY)


def available_features() -> list[str]:
    """List the available concept names."""
    return sorted(_REGISTRY)
