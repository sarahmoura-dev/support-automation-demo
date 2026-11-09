"""Intent classification for incoming customer messages.

Rule-based by default (no API key needed). An LLM classifier can be plugged in
through the `Classifier` interface, see README.
"""
import re
import unicodedata
from dataclasses import dataclass

RULES = {
    "pricing": ["price", "cost", "quote", "how much", "preco", "orcamento", "valor"],
    "schedule": ["schedule", "appointment", "book", "reschedule", "agendar", "horario"],
    "support": ["problem", "error", "broken", "not working", "help", "erro", "ajuda"],
    "cancel": ["cancel", "refund", "cancelar", "reembolso"],
}
URGENT = ["urgent", "asap", "immediately", "urgente", "agora"]


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


@dataclass
class Result:
    intent: str
    urgent: bool
    confidence: float


class RuleClassifier:
    def classify(self, text: str) -> Result:
        t = _norm(text)
        scores = {
            intent: sum(1 for k in kws if re.search(r"\b" + re.escape(k), t))
            for intent, kws in RULES.items()
        }
        best = max(scores, key=scores.get)
        total = sum(scores.values())
        urgent = any(re.search(r"\b" + k, t) for k in URGENT)
        if total == 0:
            return Result("other", urgent, 0.0)
        return Result(best, urgent, round(scores[best] / total, 2))
