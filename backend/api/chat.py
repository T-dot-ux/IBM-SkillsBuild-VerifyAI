from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from api.auth import get_current_user
from models.schema import User
import asyncio
from schemas.messages import AgentMessage
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# Agents will be started by main.py lifespan

@router.post("/")
async def chat_with_mascot(request: Request, chat_req: ChatRequest, current_user: User = Depends(get_current_user)):
    # This route will act as a quick proxy to get a threat assessment from the user's input (URL or text)
    job_id = str(uuid.uuid4())
    bus = request.app.state.bus
    
    # We send it directly to the decision agent or threat agent as a short-circuit for chat
    # To do this cleanly, we can use the ThreatDetectionAgent and DecisionAgent sequentially
    
    # Send to Threat Agent
    await bus.publish(AgentMessage(
        sender="API",
        recipient="ThreatDetectionAgent",
        type="ANALYZE_THREATS",
        job_id=job_id,
        payload={"info": {"raw_text": chat_req.message}}
    ))
    
    # Wait for threat assessment
    await asyncio.sleep(1) # Fake delay, but ideally we'd listen for response
    
    # For now, let's just use Gemini directly here since we have the key, to provide instant chat response.
    # The actual agents are background tasks.
    from google import genai
    from core.security import decrypt_api_key
    
    try:
        api_key = decrypt_api_key(current_user.encrypted_gemini_key)
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are a highly capable AI security mascot named 'VerifyAI Copilot'. 
        The user has asked you: "{chat_req.message}"
        
        If they provided a URL or QR content, assess the risk. If they are just chatting, respond conversationally.
        Keep your response under 3 sentences. State the risk level (LOW, MODERATE, HIGH, CRITICAL) at the very start if applicable.
        """
        
        # Try multiple models — broadest free-tier coverage
        models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"]
        response = None
        for m in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                break
            except Exception as model_err:
                print(f"[ChatAPI] Model {m} failed: {model_err}")
                continue
                
        if not response:
            return {
                "reply": "⚠️ I've hit my free API quota for today. The verification pipeline (rule-based heuristics) still works for file uploads! For full AI chat, please try again in a few minutes or enable billing on your Google AI Studio key.",
                "risk_level": "UNKNOWN"
            }
            
        reply = response.text
        
        risk_level = "LOW"
        if "HIGH" in reply: risk_level = "HIGH"
        if "CRITICAL" in reply: risk_level = "CRITICAL"
        if "MODERATE" in reply: risk_level = "MODERATE"
        
        return {"reply": reply, "risk_level": risk_level}
    except Exception as e:
        return {"reply": f"Sorry, I encountered an error: {e}", "risk_level": "UNKNOWN"}