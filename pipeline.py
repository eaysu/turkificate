"""Pipeline (Chain) and TurkishNormalizer (Facade).

The Pipeline applies the selected normalizers IN ORDER. TurkishNormalizer brings
together name-based selection, ordering and per-concept options behind one API.
"""

from .base import Normalizer, get_registry
from . import normalizers as _n  # noqa: F401  (import triggers registration)

__all__ = ["Pipeline", "TurkishNormalizer", "DEFAULT_ORDER", "ALL"]

#: Sentinel value to select every registered concept.
ALL = "all"

# Default execution order.
# emails/urls first so raw @ and dots are consumed before the symbol normalizer.
# Number-bearing concepts run before bare "numbers" to avoid double conversion.
DEFAULT_ORDER = [
    "emails",
    "urls",
    "dates",
    "times",
    "percent",
    "currency",
    "ordinals",
    "units",
    "numbers",
    "abbreviations",
    "symbols",
    "whitespace",
]


class Pipeline:
    """An immutable chain that runs a sequence of normalizers in order."""

    def __init__(self, normalizers: list[Normalizer]):
        self._normalizers = list(normalizers)

    def __call__(self, text: str) -> str:
        for normalizer in self._normalizers:
            text = normalizer.apply(text)
        return text

    @property
    def steps(self) -> list[str]:
        return [n.name for n in self._normalizers]

    def __repr__(self) -> str:
        return f"Pipeline({' -> '.join(self.steps)})"


class TurkishNormalizer:
    """Main entry point for Turkish text normalization (Facade).

    Parameters
    ----------
    features : concept names to use. Accepts:
        - ``None`` (default) or ``"all"`` -> every registered concept
        - a list such as ``["numbers", "dates"]`` (or a list containing ``"all"``)
        - a single concept name as a string
    order : a custom execution order (only selected concepts are considered).
    options : per-concept options, e.g. ``{"times": {"prefix_hour": True}}``.

    Examples
    --------
    >>> tn = TurkishNormalizer(features=["numbers", "dates"])
    >>> tn.normalize("15.03.2024 tarihinde 3 elma aldım.")
    'on beş Mart iki bin yirmi dört tarihinde üç elma aldım.'

    >>> TurkishNormalizer(features="all").normalize("%50")
    'yüzde elli'
    """

    def __init__(self, features=None, *, order=None, options=None):
        registry = get_registry()
        options = options or {}

        selected = self._resolve_features(features, registry)

        unknown = [f for f in selected if f not in registry]
        if unknown:
            raise ValueError(
                f"Unknown concept(s): {unknown}. "
                f"Available: {sorted(registry)} (or {ALL!r})"
            )

        # 'whitespace' is always appended for final cleanup, even if not selected.
        if "whitespace" not in selected and "whitespace" in registry:
            selected.append("whitespace")

        sequence = order or DEFAULT_ORDER
        ordered = [name for name in sequence if name in selected]
        # Append any selected concept that is not present in the order.
        ordered += [name for name in selected if name not in ordered]

        self.features = ordered
        normalizers = [registry[name](**options.get(name, {})) for name in ordered]
        self._pipeline = Pipeline(normalizers)

    @staticmethod
    def _resolve_features(features, registry) -> list[str]:
        if features is None or features == ALL:
            return list(registry)
        if isinstance(features, str):
            return list(registry) if features == ALL else [features]
        features = list(features)
        if ALL in features:
            return list(registry)
        return features

    def normalize(self, text: str) -> str:
        return self._pipeline(text)

    def __call__(self, text: str) -> str:
        return self._pipeline(text)

    def __repr__(self) -> str:
        return f"TurkishNormalizer({self._pipeline!r})"
