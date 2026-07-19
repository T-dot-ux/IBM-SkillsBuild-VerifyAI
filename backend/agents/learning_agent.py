import asyncio
import json
import os
import math
from agents.base_agent import BaseAgent
from schemas.messages import AgentMessage
# Use google generative ai for embeddings
import google.generativeai as genai

def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

class LearningAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__("LearningAgent", message_bus)
        self.memory_file = "scam_memory.json"
        self._load_memory()
        
    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                self.memory = json.load(f)
        else:
            self.memory = []
            
    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f)

    def _get_embedding(self, text: str):
        # Fallback dummy embedding for pure local testing if Gemini key is missing
        # In a real environment, this calls genai.embed_content
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception:
            # Fallback mock embedding (length 10) based on string length to allow it to run without keys
            val = float(len(text) % 100) / 100.0
            return [val] * 10

    async def process_message(self, message: AgentMessage):
        
        # 1. Store memory when a decision is finalized
        if message.type == "DECISION_COMPLETE":
            job_id = message.job_id
            payload = message.payload
            
            if payload.get("riskLevel") in ["HIGH", "CRITICAL"]:
                summary = payload.get("reasoningChain", "Unknown scam pattern")
                print(f"[{self.name}] Memorizing high-risk scam pattern for job {job_id}...")
                
                embedding = self._get_embedding(summary)
                
                self.memory.append({
                    "job_id": job_id,
                    "text": summary,
                    "embedding": embedding,
                    "verdict": payload.get("verdict")
                })
                self._save_memory()
                print(f"[{self.name}] Successfully memorized pattern.")
                
        # 2. Recall memory when new input is parsed
        elif message.type == "INPUT_PARSED":
            job_id = message.job_id
            extracted_text = message.payload.get("extracted_text", "")
            
            if not extracted_text or not self.memory:
                return
                
            print(f"[{self.name}] Searching long-term memory for similar patterns...")
            
            query_embedding = self._get_embedding(extracted_text)
            
            best_match = None
            best_score = -1
            
            for item in self.memory:
                score = cosine_similarity(query_embedding, item["embedding"])
                if score > best_score:
                    best_score = score
                    best_match = item
                    
            # 0.95 is a high cosine similarity threshold
            if best_match and best_score > 0.95:
                print(f"[{self.name}] Match found! Similarity: {best_score}. Emitting Red Flag.")
                await self.send_message(
                    recipient="MasterAgent", 
                    msg_type="EVIDENCE_SUBMISSION",
                    payload={
                        "evidence_type": "RED_FLAG",
                        "severity": 0.95,
                        "finding": f"CRITICAL: This exact text strongly matches a previously verified scam (Job ID: {best_match.get('job_id')}). Educational tip: Never trust recurring identical templates."
                    },
                    job_id=job_id,
                    reply_to=self.name
                )
            else:
                print(f"[{self.name}] No historical match found (Max Similarity: {best_score}).")