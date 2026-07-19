import asyncio
import os
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from google import genai
from google.genai import types

class InputIntelligenceAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("InputIntelligenceAgent", message_bus)

    async def process_message(self, message: AgentMessage):
        if message.type == "EXTRACT_INFO":
            job_id = message.job_id
            payload = message.payload
            data = payload.get("data", "")
            api_key = payload.get("gemini_api_key")
            
            print(f"[{self.name}] Extracting info for job {job_id}")
            
            extracted_text = ""
            metadata = {
                "type": "text", 
                "qr_codes": [],
                "barcodes": [],
                "links": [],
                "file_type": "unknown",
                "anomalies": []
            }
            
            # 1. Parse File if it's a file path
            file_path = None
            if isinstance(data, str) and data.startswith("File path: "):
                file_path = data.replace("File path: ", "").strip()
            
            if file_path and os.path.exists(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                metadata["file_type"] = ext
                
                # Try local text extraction first (e.g. PyMuPDF or Docx)
                if ext == ".pdf":
                    try:
                        doc = fitz.open(file_path)
                        text_list = []
                        for page in doc:
                            text_list.append(page.get_text())
                        extracted_text = "\n".join(text_list).strip()
                        
                        # Look for font anomalies
                        font_names = []
                        for page in doc:
                            for font in page.get_fonts():
                                font_names.append(font[3])
                        # If weird/mixed fonts (e.g., Arial combined with custom comic fonts on official letterheads)
                        if len(set(font_names)) > 10:
                            metadata["anomalies"].append("High font variation (potential spoofing).")
                            
                    except Exception as pdf_err:
                        print(f"[{self.name}] Local PDF parsing failed: {pdf_err}")
                        metadata["anomalies"].append("PDF structure is corrupted or unreadable locally.")
                        
                elif ext == ".docx":
                    try:
                        doc = DocxDocument(file_path)
                        text_list = [p.text for p in doc.paragraphs]
                        extracted_text = "\n".join(text_list).strip()
                    except Exception as docx_err:
                        print(f"[{self.name}] Word parsing failed: {docx_err}")
                
                # If it's an image, or a scanned PDF (very short extracted text), use Gemini's Multimodal API
                is_scanned = (ext == ".pdf" and len(extracted_text) < 100)
                is_image = ext in [".png", ".jpg", ".jpeg"]
                
                if (is_scanned or is_image) and api_key:
                    try:
                        print(f"[{self.name}] Using Gemini Multimodal to analyze {ext} file...")
                        client = genai.Client(api_key=api_key)
                        
                        mime_type = "application/pdf" if ext == ".pdf" else f"image/{ext.replace('.', '')}"
                        if mime_type == "image/jpg":
                            mime_type = "image/jpeg"
                            
                        # Prompt Gemini to extract text and analyze visual aspects (QR, barcode, etc)
                        prompt = """
                        You are a preprocessing agent for a document verification pipeline. 
                        Analyze this document/image.
                        1. Extract ALL readable text.
                        2. Look closely for any QR codes or barcodes. If found, extract their target value/contents.
                        3. Identify any URLs or links written on the page.
                        
                        Format your response as a JSON object:
                        {
                            "text": "all extracted text...",
                            "qr_codes": ["contents of qr code 1", ...],
                            "barcodes": ["contents of barcode 1", ...],
                            "links": ["http://...", ...]
                        }
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                types.Part.from_bytes(
                                    data=open(file_path, "rb").read(),
                                    mime_type=mime_type
                                ),
                                prompt
                            ]
                        )
                        
                        # Parse JSON response
                        import json
                        clean_text = response.text.replace("```json", "").replace("```", "").strip()
                        ai_extracted = json.loads(clean_text)
                        
                        extracted_text = ai_extracted.get("text", "")
                        metadata["qr_codes"].extend(ai_extracted.get("qr_codes", []))
                        metadata["barcodes"].extend(ai_extracted.get("barcodes", []))
                        metadata["links"].extend(ai_extracted.get("links", []))
                        
                    except Exception as multimodal_err:
                        print(f"[{self.name}] Gemini Multimodal analysis failed: {multimodal_err}")
                        metadata["anomalies"].append(f"Multimodal OCR failed: {multimodal_err}")
            
            else:
                # Direct string data (e.g. website link, qr text)
                extracted_text = data if isinstance(data, str) else str(data)
                if extracted_text.startswith("http://") or extracted_text.startswith("https://"):
                    metadata["file_type"] = "link"
                    metadata["links"].append(extracted_text)
                else:
                    metadata["file_type"] = "text"
            
            # Simple link extraction from plain text if not already populated
            if not metadata["links"]:
                import re
                urls = re.findall(r'(https?://[^\s]+)', extracted_text)
                metadata["links"].extend(urls)
                
            result = {
                "raw_text": extracted_text,
                "metadata": metadata
            }
            
            if message.reply_to:
                await self.send_message(
                    recipient=message.reply_to,
                    msg_type="INFO_EXTRACTED",
                    payload=result,
                    job_id=job_id,
                    reply_to=self.name
                )
