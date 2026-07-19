from typing import List, Dict


class RiskScoringEngine:
    """
    Calculates the final Trust Score dynamically.

    Scoring Formula
    ---------------
    1. Base score   = ai_score  (0-100), provided by GeminiAgent.
    2. Rule penalty = number_of_rule_flags × PENALTY_PER_FLAG points.
    3. Final score  = max(0, base_score - rule_penalty)

    Why no mocked partial scores?
    - Previously, metadata_score / ocr_consistency / integrity_score each
      contributed a static 50 pts, meaning a fraudulent document could always
      score 70-80+.  Those values are now excluded from the formula.
    - Rule penalties are deliberately heavy (20 pts each) so that a document
      with 3 hard rule flags loses 60 points regardless of AI optimism.
    - The AI score itself is instructed to penalise error strings and obvious
      fraud patterns before it ever reaches this engine.
    """

    PENALTY_PER_FLAG: float = 20.0

    def calculate_score(
        self,
        rule_flags: List[Dict],
        ai_analysis: Dict,
        # Legacy parameters kept for API compatibility — no longer used in math
        metadata_score: float = 100,
        ocr_consistency: float = 100,
        integrity_score: float = 100,
    ) -> float:
        # Base score from AI semantic analysis
        ai_score = float(ai_analysis.get("ai_score", 50))

        # Deterministic deductions: each hard rule flag removes 20 points
        rule_penalty = len(rule_flags) * self.PENALTY_PER_FLAG

        # Clamp to [0, 100]
        final_score = max(0.0, min(100.0, ai_score - rule_penalty))

        return round(final_score, 1)
