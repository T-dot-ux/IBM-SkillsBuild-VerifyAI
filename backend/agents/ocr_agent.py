import os
import fitz  # PyMuPDF

# Sentinel prefix used by the orchestrator to detect OCR extraction failures
OCR_FAILURE_PREFIX = "[OCR_FAILED]"


class OCRAgent:
    """
    Extracts text from uploaded documents.

    Failure contract
    ----------------
    If text cannot be extracted (unsupported type, Tesseract missing, etc.) the
    method returns a string that STARTS WITH ``OCR_FAILURE_PREFIX``.  The
    orchestrator checks for this prefix and short-circuits the pipeline
    (trust_score = 0, status = FAILED) instead of passing junk to the AI.
    """

    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""

        try:
            if ext == ".pdf":
                doc = fitz.open(file_path)
                for page in doc:
                    extracted_text += page.get_text()

                # If no text was found, it might be an image-based PDF. Try OCR on pages.
                if not extracted_text.strip():
                    print("[OCRAgent] PDF text empty. Attempting OCR on pages...")
                    from PIL import Image
                    try:
                        import pytesseract
                        tesseract_available = True
                    except ImportError:
                        tesseract_available = False

                    # Try Gemini Fallback first, then Tesseract
                    try:
                        from agents.gemini_agent import GeminiAgent
                        gemini = GeminiAgent()
                        has_gemini = bool(gemini._client)
                    except ImportError:
                        has_gemini = False

                    prompt = (
                        "Extract and return all readable text from this image document. "
                        "Do not add any comments, explanations, markdown formatting, or headers. "
                        "Just return the exact text content found in the image."
                    )

                    for page in doc:
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                        page_text = ""
                        if has_gemini:
                            for model_name in gemini.supported_models:
                                try:
                                    response = gemini._client.models.generate_content(
                                        model=model_name,
                                        contents=[img, prompt]
                                    )
                                    if response and response.text:
                                        page_text = response.text
                                        break
                                except Exception:
                                    continue
                        
                        if not page_text and tesseract_available:
                            page_text = pytesseract.image_to_string(img)
                        
                        if page_text:
                            extracted_text += page_text + "\n"

                doc.close()

                # A PDF that yields no text is still a failure
                if not extracted_text.strip():
                    return (
                        f"{OCR_FAILURE_PREFIX} PDF contained no extractable text. "
                        "It may be a scanned image PDF. Re-upload as an image or "
                        "provide a text-based PDF."
                    )

            elif ext in (".png", ".jpg", ".jpeg", ".webp"):
                try:
                    import pytesseract
                    from PIL import Image

                    img = Image.open(file_path)
                    extracted_text = pytesseract.image_to_string(img)

                    if not extracted_text.strip():
                        return (
                            f"{OCR_FAILURE_PREFIX} Tesseract ran successfully but "
                            "extracted no text from the image. The image may be blank, "
                            "too low-resolution, or contain only graphics."
                        )

                except (ImportError, Exception) as err:
                    print(f"[OCRAgent] Local OCR failed ({type(err).__name__}): {err}. Attempting Gemini fallback OCR...")
                    try:
                        from PIL import Image
                        from agents.gemini_agent import GeminiAgent
                        
                        img = Image.open(file_path)
                        gemini = GeminiAgent()
                        
                        if not gemini._client:
                            raise ValueError("Gemini API key is not configured.")

                        prompt = (
                            "Extract and return all readable text from this image document. "
                            "Do not add any comments, explanations, markdown formatting, or headers. "
                            "Just return the exact text content found in the image."
                        )
                        
                        response = None
                        for model_name in gemini.supported_models:
                            try:
                                response = gemini._client.models.generate_content(
                                    model=model_name,
                                    contents=[img, prompt]
                                )
                                if response and response.text:
                                    break
                            except Exception as model_err:
                                print(f"[OCRAgent] Gemini fallback model {model_name} failed: {model_err}")
                                continue
                        
                        if response and response.text:
                            extracted_text = response.text
                            if not extracted_text.strip():
                                raise ValueError("Gemini returned empty text.")
                            print(f"[OCRAgent] Gemini OCR fallback succeeded! Extracted {len(extracted_text)} characters.")
                        else:
                            raise RuntimeError("All Gemini models failed to process the image.")

                    except Exception as fallback_err:
                        print(f"[OCRAgent] Gemini OCR fallback failed: {fallback_err}")
                        if isinstance(err, ImportError):
                            return (
                                f"{OCR_FAILURE_PREFIX} pytesseract or Pillow is not installed. "
                                f"Image OCR requires 'pip install pytesseract Pillow' and a local Tesseract binary. "
                                f"(Gemini fallback also failed: {fallback_err})"
                            )
                        else:
                            return (
                                f"{OCR_FAILURE_PREFIX} Image OCR failed: {err}. "
                                f"Ensure Tesseract is installed and on PATH. "
                                f"(Gemini fallback also failed: {fallback_err})"
                            )

            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    extracted_text = f.read()

                if not extracted_text.strip():
                    return f"{OCR_FAILURE_PREFIX} The uploaded text file is empty."

            elif ext == ".docx":
                try:
                    import docx
                    word_doc = docx.Document(file_path)
                    extracted_text = "\n".join([para.text for para in word_doc.paragraphs])
                    if not extracted_text.strip():
                        return f"{OCR_FAILURE_PREFIX} The uploaded Word document is empty."
                except Exception as e:
                    return f"{OCR_FAILURE_PREFIX} Failed to read Word document: {e}"

            else:
                return (
                    f"{OCR_FAILURE_PREFIX} Unsupported file type '{ext}'. "
                    "Accepted formats: PDF, PNG, JPG, JPEG, WEBP, TXT."
                )

        except Exception as e:
            print(f"[OCRAgent] Unexpected OCR error: {e}")
            return f"{OCR_FAILURE_PREFIX} Unexpected extraction error: {e}"

        return extracted_text
