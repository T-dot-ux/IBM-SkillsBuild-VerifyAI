import json
from .ocr_agent import OCR_FAILURE_PREFIX
from .rule_agent import RuleEngineAgent
from .scoring_engine import RiskScoringEngine
from .gemini_agent import GeminiAgent

# ---------------------------------------------------------------------------
# Agent singletons
# ---------------------------------------------------------------------------
rule_engine = RuleEngineAgent()
scoring_engine = RiskScoringEngine()
gemini_agent = GeminiAgent()


def run_adk_pipeline(extracted_text: str) -> dict:
    """
    Run the full VerifyAI analysis pipeline.

    Short-circuits immediately if OCR extraction failed, returning a zero-score
    FAILED result without wasting an AI API call on an error string.

    Steps (happy path):
    1. Classify document category via Gemini.
    2. Run deterministic rule engine (context-aware per document type).
    3. Run AI semantic trust analysis via Gemini.
    4. Calculate final trust score (AI base − rule penalties).
    5. Combine and return all evidence.
    """
    print("[Pipeline] Starting ADK pipeline…")

    # ------------------------------------------------------------------
    # Gate 1: OCR Failure Short-Circuit
    # ------------------------------------------------------------------
    if extracted_text.startswith(OCR_FAILURE_PREFIX):
        error_detail = extracted_text[len(OCR_FAILURE_PREFIX):].strip()
        print(f"[Pipeline] OCR failed — short-circuiting. Reason: {error_detail}")
        return {
            "ai_score": 0,
            "ai_flags": [f"Document extraction failed: {error_detail}"],
            "ai_positive": [],
            "summary": (
                "The document could not be extracted. No content was available for "
                "analysis. Trust score is 0."
            ),
            "recommendation": "REJECT: Re-upload a valid, readable document.",
            "trust_score": 0,
            "ocr_failed": True,
        }

    # ------------------------------------------------------------------
    # Step 1: Classify Document
    # ------------------------------------------------------------------
    category = gemini_agent.classify_document(extracted_text)
    print(f"[Pipeline] Document classified as: {category}")

    # ------------------------------------------------------------------
    # Step 2: Deterministic Rule Engine (context-aware)
    # ------------------------------------------------------------------
    rule_flags_raw = rule_engine.evaluate(extracted_text, category)
    print(f"[Pipeline] Rule flags detected: {len(rule_flags_raw)}")

    # ------------------------------------------------------------------
    # Step 3: AI Semantic Trust Analysis
    # ------------------------------------------------------------------
    ai_analysis = gemini_agent.analyze_trust(extracted_text, category)
    print(f"[Pipeline] AI score: {ai_analysis.get('ai_score')}")

    # ------------------------------------------------------------------
    # Step 4: Risk Scoring Engine
    # ------------------------------------------------------------------
    trust_score = scoring_engine.calculate_score(
        rule_flags=rule_flags_raw,
        ai_analysis=ai_analysis,
    )
    print(f"[Pipeline] Final trust score: {trust_score}")

    # ------------------------------------------------------------------
    # Step 5: Combine Evidence
    # ------------------------------------------------------------------
    # Merge AI flags + formatted rule flags into a single list
    combined_flags = list(ai_analysis.get("ai_flags", []))
    for flag in rule_flags_raw:
        combined_flags.append(
            f"[{flag['category']}] {flag['description']}"
        )

    summary = ai_analysis.get("summary", "Document analyzed successfully.")
    recommendation = ai_analysis.get("recommendation", "Review completed.")

    # Override recommendation based on final score thresholds
    if trust_score < 40:
        recommendation = "REJECT: High risk of fraud detected."
    elif trust_score < 70:
        recommendation = "MANUAL REVIEW: Moderate risk factors detected."
    elif trust_score >= 85 and "APPROVE" not in recommendation.upper():
        recommendation = "APPROVE: Document appears authentic."

    return {
        "ai_score": ai_analysis.get("ai_score", 50),
        "ai_flags": combined_flags,
        "ai_positive": ai_analysis.get("ai_positive", []),
        "summary": summary,
        "recommendation": recommendation,
        "trust_score": trust_score,
        "document_category": category,
        "ocr_failed": False,
    }
