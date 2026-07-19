import datetime
from google import genai
from google.genai import types
from utils.config import settings
from typing import Dict

# Sentinel strings that indicate OCR failure rather than real document content
OCR_ERROR_SENTINELS = [
    "[image ocr failed",
    "tesseract not installed",
    "[unsupported file type",
    "[image ocr error",
]

def _is_ocr_error(text: str) -> bool:
    """Returns True if the extracted text is an OCR error message, not real content."""
    lowered = text.strip().lower()
    return any(sentinel in lowered for sentinel in OCR_ERROR_SENTINELS)


class GeminiAgent:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self._client = None

        # Models to try in order of preference
        self.supported_models = [
            "gemini-3.5-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-flash-latest",
        ]

    def _generate(self, model_name: str, prompt: str, response_schema) -> Dict:
        """
        Generate content using the modern google.genai SDK with strict JSON schema.
        Falls back gracefully if a model is unavailable.
        """
        response = self._client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
        return response.parsed

    def _generate_with_fallback(self, prompt: str, response_schema) -> Dict:
        """Try each model in order, returning the first successful result."""
        if not self._client:
            raise ValueError("GEMINI_API_KEY is not configured.")

        last_exception = None
        for model_name in self.supported_models:
            try:
                result = self._generate(model_name, prompt, response_schema)
                if result is not None:
                    return result
            except Exception as e:
                last_exception = e
                print(f"[GeminiAgent] Model {model_name} failed: {e}. Trying next…")
                continue

        raise RuntimeError(f"All Gemini models failed. Last error: {last_exception}")

    # -------------------------------------------------------------------------
    # Classification
    # -------------------------------------------------------------------------

    def classify_document(self, extracted_text: str) -> str:
        """
        Classifies the document into one of the known DocumentCategory values.
        Uses a strict response_schema to guarantee valid JSON.
        """
        if not self._client:
            return "UNKNOWN"

        if _is_ocr_error(extracted_text):
            return "UNKNOWN"

        prompt = f"""
        You are an expert document classifier.
        Classify the following text into EXACTLY ONE of these categories:
        JOB_OFFER, CERTIFICATE, PAYMENT_PROOF, LEGAL_DOCUMENT, NEWS_MEDIA, UNKNOWN.

        Text to classify (first 3000 characters):
        {extracted_text[:3000]}
        """

        schema = {"type": "object", "properties": {"category": {"type": "string"}}, "required": ["category"]}

        try:
            data = self._generate_with_fallback(prompt, schema)
            category = str(data.get("category", "UNKNOWN")).upper()
            valid = {"JOB_OFFER", "CERTIFICATE", "PAYMENT_PROOF", "LEGAL_DOCUMENT", "NEWS_MEDIA", "UNKNOWN"}
            return category if category in valid else "UNKNOWN"
        except Exception as e:
            print(f"[GeminiAgent] Classification failed: {e}")
            return "UNKNOWN"

    # -------------------------------------------------------------------------
    # Trust Analysis
    # -------------------------------------------------------------------------

    def analyze_trust(self, extracted_text: str, document_category: str) -> Dict:
        """
        Performs semantic analysis to find hidden red flags, positive indicators,
        and generate an AI trust score.

        Uses response_schema enforcement — no string manipulation required.
        """
        if not self._client:
            return {
                "ai_score": 100,
                "ai_flags": [],
                "ai_positive": [],
                "summary": "AI Analysis bypassed (No API Key).",
                "recommendation": "Manual review required.",
            }

        # If OCR produced an error string, immediately fail with score 0
        if _is_ocr_error(extracted_text):
            return {
                "ai_score": 0,
                "ai_flags": [
                    "Document content could not be extracted (OCR failure or unsupported format). "
                    "The raw error message was passed as input — this is NOT a real document."
                ],
                "ai_positive": [],
                "summary": (
                    "The document extraction failed entirely. The text received is an OCR error "
                    "message, not actual document content. Trust score is set to 0."
                ),
                "recommendation": "REJECT: Document could not be extracted. Re-upload a valid file.",
            }

        current_date = datetime.date.today().strftime("%d %b %Y")

        prompt = f"""
You are VerifyAI, a highly advanced fraud detection AI.
CRITICAL CONTEXT: Today's date is {current_date}.

You are analyzing text extracted from a document classified as: {document_category}.

IMPORTANT SCORING RULES:
- If the text you receive is an error message (e.g. "Tesseract not installed", "OCR failed",
  "[Image OCR failed...]"), assign ai_score = 0 immediately. This is NOT a real document.
- If the document contains strong fraud signals (upfront fees, unverifiable claims, 
  pressure tactics, free email for corporate identity), assign ai_score ≤ 30.
- Only assign ai_score ≥ 80 if the document has clear, consistent, professional credibility.

Analyze the following text thoroughly for:
1. Subtle red flags: grammar inconsistencies, unrealistic claims, pressure tactics,
   suspicious contact methods, requests for money/personal info.
2. Positive indicators: official letterhead references, verifiable contact info,
   professional tone, realistic salary/timeline details.

Text to analyze (up to 5000 characters):
{extracted_text[:5000]}
"""

        schema = {
            "type": "object",
            "properties": {
                "ai_score": {
                    "type": "integer",
                    "description": "Trust score from 0 (absolute fraud) to 100 (perfectly authentic).",
                },
                "ai_flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of red flags or suspicious signals found.",
                },
                "ai_positive": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of credibility indicators found.",
                },
                "summary": {
                    "type": "string",
                    "description": "A 2-sentence summary of findings.",
                },
                "recommendation": {
                    "type": "string",
                    "description": "A 1-sentence strict recommendation.",
                },
            },
            "required": ["ai_score", "ai_flags", "ai_positive", "summary", "recommendation"],
        }

        try:
            result = self._generate_with_fallback(prompt, schema)
            # Clamp the score to [0, 100]
            result["ai_score"] = max(0, min(100, int(result.get("ai_score", 50))))
            return result
        except Exception as e:
            print(f"[GeminiAgent] AI Analysis failed: {e}")
            return {
                "ai_score": 50,
                "ai_flags": [f"AI Analysis failed to process the document: {str(e)}"],
                "ai_positive": [],
                "summary": "AI Analysis encountered an error and could not complete.",
                "recommendation": "Please review the document manually.",
            }
