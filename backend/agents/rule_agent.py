import re
from typing import List, Dict

# ---------------------------------------------------------------------------
# Rule categories that are UNIVERSAL (apply to any document type)
# ---------------------------------------------------------------------------
UNIVERSAL_RULES: Dict[str, List[str]] = {
    "suspicious_contact": [
        r"(?i)\b(telegram|whatsapp)\s*(?:app)?\s*:\s*\+?\d+\b",
        r"(?i)[a-zA-Z0-9._%+-]+@(yahoo|hotmail|gmail|protonmail)\.com",
    ],
}

# ---------------------------------------------------------------------------
# Rule categories that are DOCUMENT-TYPE-SPECIFIC
# Key = DocumentCategory enum value | "DEFAULT" (fallback for unlisted types)
# ---------------------------------------------------------------------------
DOCUMENT_TYPE_RULES: Dict[str, Dict[str, List[str]]] = {
    "JOB_OFFER": {
        "upfront_payment": [
            r"(?i)\b(processing fee|upfront payment|refundable deposit|equipment fee|onboarding fee|training fee)\b",
            r"(?i)\bpay\s+\$?(\d+)\s+before\s+starting\b",
            r"(?i)\b(send|wire|transfer)\s+\$?(\d+)\s+(to|via)\b",
        ],
        "urgency": [
            r"(?i)\b(act fast|immediate action required|limited time offer|urgent response|respond within 24 hours)\b",
        ],
        "vague_company": [
            r"(?i)\bwork from home\s+(unlimited|uncapped)\s+(earning|income|salary)\b",
            r"(?i)\bno experience (required|necessary|needed)\b",
        ],
    },
    "CERTIFICATE": {
        "forgery_indicators": [
            r"(?i)\b(photoshopped|edited|modified|altered)\b",
            r"(?i)\bvalid (until|through)\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # check for expired certs
        ],
    },
    "LEGAL_DOCUMENT": {
        "missing_structure": [
            r"(?i)\b(whereas|therefore|in witness whereof)\b",  # positive signals; absence is a flag
        ],
        "upfront_payment": [
            r"(?i)\b(advance fee|upfront retainer|non-refundable deposit)\b",
        ],
    },
    "PAYMENT_PROOF": {
        "suspicious_amounts": [
            r"(?i)\b(processing fee|handling fee|clearance fee)\b",
        ],
    },
    "DEFAULT": {
        "urgency": [
            r"(?i)\b(act fast|immediate action required|limited time offer|urgent response)\b",
        ],
    },
}


class RuleEngineAgent:
    """
    Deterministic rule-based fraud detection.
    
    Runs universal rules on ALL documents, plus document-type-specific rules
    based on the classified DocumentCategory. This avoids false positives from
    applying job-offer checks to legal documents and vice-versa.
    """

    def evaluate(self, text: str, document_type: str) -> List[Dict]:
        flags: List[Dict] = []

        # 1. Universal rules — always run
        flags.extend(self._apply_ruleset(text, UNIVERSAL_RULES))

        # 2. Document-type-specific rules
        specific_rules = DOCUMENT_TYPE_RULES.get(
            document_type.upper(),
            DOCUMENT_TYPE_RULES["DEFAULT"]
        )
        flags.extend(self._apply_ruleset(text, specific_rules))

        return flags

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_ruleset(text: str, ruleset: Dict[str, List[str]]) -> List[Dict]:
        """Apply a dict of {category: [patterns]} to text, returning flag dicts."""
        flags: List[Dict] = []
        seen_matches: set = set()  # de-duplicate identical matched strings

        for rule_category, patterns in ruleset.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    matched_text = match.group(0).strip()
                    key = (rule_category, matched_text.lower())
                    if key in seen_matches:
                        continue
                    seen_matches.add(key)
                    flags.append({
                        "category": rule_category,
                        "matched_text": matched_text,
                        "description": (
                            f"Suspicious pattern detected [{rule_category}]: "
                            f"'{matched_text}'"
                        ),
                    })

        return flags
