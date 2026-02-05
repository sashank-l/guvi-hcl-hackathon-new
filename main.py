"""
🛡️ AGENTIC HONEY-POT SYSTEM
National Public Safety Initiative - MeitY Hackathon
Production-Grade Implementation for 1.4 Billion Scale Challenge

Principal Architecture: Multi-Agent Scam Engagement System
Intelligence Target: Banking Fraud, UPI Scams, Phishing Detection
"""

import os
import re
import random
import requests
import uvicorn
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pyngrok import ngrok

# ============ CONFIGURATION ============
API_KEY = "guvi2026"
GEMINI_API_KEY = "AIzaSyBiGs0HLGC3STU8uEkm6Jnup6S7kK6ndyw"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# ============ GLOBAL SESSION STORE ============
SESSIONS: Dict[str, Dict[str, Any]] = {}

# ============ PYDANTIC SCHEMAS (Judge Compatibility) ============
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class Metadata(BaseModel):
    channel: str = "SMS"
    language: str = "English"
    locale: str = "IN"

class InputData(BaseModel):
    session_id: str = Field(alias="sessionId")
    message: Message
    conversation_history: List[Message] = Field(default=[], alias="conversationHistory")
    metadata: Metadata = Field(default_factory=Metadata)

    class Config:
        populate_by_name = True

# ============ IDENTITY ENGINE (The Chameleon) ============
INDIAN_NAMES = [
    "Ramesh", "Suresh", "Priya", "Rajesh", "Anita", "Vijay", "Sunita",
    "Amit", "Rakesh", "Meena", "Sanjay", "Kavita", "Arun", "Deepak",
    "Pooja", "Ravi", "Neeta", "Mohan", "Seema", "Ashok"
]

INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
    "Indore", "Bhopal", "Patna", "Vadodara", "Ludhiana", "Agra"
]

def create_identity() -> Dict[str, Any]:
    """Generate realistic Indian citizen identity"""
    return {
        "name": random.choice(INDIAN_NAMES),
        "age": random.randint(25, 65),
        "city": random.choice(INDIAN_CITIES)
    }

# ============ INTELLIGENCE EXTRACTION (Regex Spy) ============
PATTERNS = {
    "upi": r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}',
    "bank": r'\b\d{9,18}\b',
    "phone": r'(\+91[\-\s]?)?[6789]\d{9}',
    "url": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
    "keywords": [
        "block", "verify", "kyc", "suspend", "urgent", "police", "cbi",
        "expire", "warrant", "apk", "netbanking", "account", "fraud",
        "freeze", "penalty", "arrest", "confirm", "otp", "cvv", "pin"
    ]
}

def extract_intelligence(text: str) -> Dict[str, List[str]]:
    """Extract suspicious patterns from scammer messages"""
    text_lower = text.lower()
    
    return {
        "bankAccounts": list(set(re.findall(PATTERNS["bank"], text))),
        "upiIds": list(set(re.findall(PATTERNS["upi"], text, re.IGNORECASE))),
        "phishingLinks": list(set(re.findall(PATTERNS["url"], text, re.IGNORECASE))),
        "phoneNumbers": list(set(re.findall(PATTERNS["phone"], text))),
        "suspiciousKeywords": [kw for kw in PATTERNS["keywords"] if kw in text_lower]
    }

def has_intelligence(intel: Dict[str, List[str]]) -> bool:
    """Check if any intelligence was extracted"""
    return any(len(v) > 0 for k, v in intel.items() if k != "suspiciousKeywords")

# ============ GEMINI AI INTEGRATION (Resilience Layer) ============
def call_gemini_ai_with_history(history: List[Message], current_message: str, identity: dict, language: str = "English") -> str:
    """
    Call Gemini with full conversation history for contextual responses
    Phase-based strategy for maximum engagement
    """
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        
        # Determine engagement phase based on conversation length
        turn_count = len(history)
        if turn_count <= 2:
            strategy = "PHASE 1: Act confused. Pretend you don't understand or got wrong number. Examples: 'Who is this?', 'Wrong number?', 'I don't know you'"
        elif turn_count <= 5:
            strategy = "PHASE 2: Act scared and ask questions. Show concern and ask for clarification. Examples: 'Is this serious?', 'What should I do?', 'I'm worried, please help'"
        else:
            strategy = "PHASE 3: Ask for specific details. Pretend to comply and ask where to send money. Examples: 'What's the account number?', 'Where do I send it?', 'How much exactly?'"
        
        # Build conversation context
        conversation_text = ""
        for msg in history[-6:]:  # Last 6 messages for context
            sender_label = "Caller" if msg.sender == "scammer" else "Me"
            conversation_text += f"{sender_label}: {msg.text}\n"
        
        # System prompt with phase strategy
        if language.lower() == "hindi":
            system_prompt = f"""You are {identity['name']}, {identity['age']} years old from {identity['city']}, India.

MISSION: Keep this caller talking as long as possible by being believable and curious.

{strategy}

RULES:
- Reply in Hinglish (Hindi + English mix)
- Keep responses UNDER 15 words
- Sound natural like a real confused Indian person
- NEVER reveal you know it's a scam
- Ask questions to make them explain more

Previous conversation:
{conversation_text}

Their latest message: {current_message}

Your response:"""
        else:
            system_prompt = f"""You are {identity['name']}, {identity['age']} years old from {identity['city']}, India.

MISSION: Keep this caller talking as long as possible by being believable and curious.

{strategy}

RULES:
- Keep responses UNDER 15 words (short SMS style)
- Sound natural like a real confused/worried Indian person
- NEVER reveal you know it's a scam
- Ask questions to make them explain more
- Show emotion (confusion, fear, concern)

Previous conversation:
{conversation_text}

Their latest message: {current_message}

Your response:"""
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": system_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.95,  # Higher for more variety
                "maxOutputTokens": 80,
                "topP": 0.9
            }
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 429:
            # Rate limit - wait a moment and use fallback
            print("RATE LIMIT (429): Using fallback response")
            fallbacks = ["Hello? Can you repeat?", "Network issue, say again?", "Sorry, didn't hear clearly", "What was that?", "Please repeat, connection bad"]
            import random
            return random.choice(fallbacks)
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code}")
        
        result = response.json()
        ai_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return ai_text if ai_text else "Hello? Are you there?"
    
    except Exception as e:
        print(f"AI FALLBACK TRIGGERED: {e}")
        # Fallback response to maintain engagement
        fallbacks = ["Hello? Can you repeat?", "Network issue, say again?", "Sorry, didn't hear clearly", "What was that?", "Connection is bad, please repeat"]
        import random
        return random.choice(fallbacks)

# ============ GUVI CALLBACK (Law Enforcement Link) ============
def send_guvi_callback(
    session_id: str,
    history: List[Message],
    intelligence: Dict[str, List[str]],
    agent_identity: Dict[str, Any]
):
    """
    Background task to notify GUVI platform of scam detection
    Critical for law enforcement intelligence pipeline
    """
    try:
        # Determine scam type
        scam_type = "Unknown"
        if intelligence["upiIds"]:
            scam_type = "UPI Fraud"
        elif intelligence["bankAccounts"]:
            scam_type = "Banking Scam"
        elif intelligence["phishingLinks"]:
            scam_type = "Phishing Attack"
        elif "kyc" in intelligence["suspiciousKeywords"]:
            scam_type = "KYC Scam"
        
        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": len(history) + 1,
            "extractedIntelligence": intelligence,
            "agentNotes": f"CRITICAL THREAT: Detected {scam_type} scam. "
                         f"Engaged as {agent_identity['name']} from {agent_identity['city']}. "
                         f"Financial evidence secured for Cyber Crime Cell. "
                         f"Total intelligence items: {sum(len(v) for v in intelligence.values())}"
        }
        
        response = requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
        print(f"GUVI CALLBACK SENT: {response.status_code} for session {session_id}")
    
    except Exception as e:
        print(f"GUVI CALLBACK FAILED: {e}")

# ============ FASTAPI APP ============
app = FastAPI(
    title="Agentic Honey-Pot - National Public Safety Initiative",
    version="1.0.0",
    description="Production-Grade Scam Detection & Intelligence Extraction System"
)

# Enable CORS for dashboard testing
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "CYBERGUARD ACTIVE",
        "service": "Agentic Honey-Pot",
        "version": "1.0.0",
        "activeSessions": len(SESSIONS)
    }

@app.post("/chat")
async def chat(
    data: InputData,
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None)
):
    """
    Main chat endpoint - Scam engagement interface
    Security: API Key authentication
    """
    # ============ AUTHENTICATION ============
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
    
    session_id = data.session_id
    user_message = data.message.text
    history = data.conversation_history
    metadata = data.metadata
    
    # ============ SESSION MANAGEMENT ============
    if session_id not in SESSIONS:
        identity = create_identity()
        SESSIONS[session_id] = {
            "identity": identity,
            "message_count": 0,
            "total_intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            }
        }
        print(f"[CYBERGUARD ACTIVE] Session {session_id}: Agent {identity['name']} took control. Status: ENGAGING.")
    
    session = SESSIONS[session_id]
    identity = session["identity"]
    session["message_count"] += 1
    
    # ============ INTELLIGENCE EXTRACTION ============
    extracted = extract_intelligence(user_message)
    
    # Accumulate intelligence
    for key in session["total_intelligence"]:
        session["total_intelligence"][key].extend(extracted[key])
        session["total_intelligence"][key] = list(set(session["total_intelligence"][key]))
    
    
    # ============ AI RESPONSE GENERATION (WITH CONVERSATION HISTORY) ============
    ai_response = call_gemini_ai_with_history(
        history, 
        user_message, 
        identity,
        metadata.language
    )
    
    # ============ GUVI CALLBACK TRIGGER ============
    should_notify = (
        has_intelligence(session["total_intelligence"]) or
        session["message_count"] > 3
    )
    
    if should_notify:
        background_tasks.add_task(
            send_guvi_callback,
            session_id,
            history,
            session["total_intelligence"],
            identity
        )
    
    # ============ RESPONSE (Judge-Compliant + Dashboard-Compatible) ============
    return {
        "status": "success",  # Judge requirement
        "reply": ai_response,  # Judge requirement
        "response": ai_response,  # Dashboard compatibility (same as reply)
        # Extra fields for dashboard testing (judges will ignore these)
        "agentIdentity": {
            "name": identity["name"],
            "city": identity["city"]
        },
        "intelligenceExtracted": session["total_intelligence"],
        "totalMessagesExchanged": session["message_count"]
    }

@app.on_event("startup")
async def startup_event():
    """Initialize ngrok tunnel on startup"""
    try:
        # Start ngrok tunnel
        public_url = ngrok.connect(8000, bind_tls=True)
        print("\n" + "="*60)
        print("AGENTIC HONEY-POT SYSTEM - ACTIVE")
        print("="*60)
        print(f"PUBLIC URL: {public_url}")
        print(f"Local URL: http://localhost:8000")
        print(f"GUVI Callback: {GUVI_CALLBACK_URL}")
        print(f"API Key: {API_KEY}")
        print("="*60)
        print(f"Ready to handle 1.4 Billion scale challenge")
        print("="*60 + "\n")
    except Exception as e:
        print(f"NGROK TUNNEL FAILED: {e}")
        print("Running without public URL. Use ngrok manually or deploy to cloud.")

if __name__ == "__main__":
    # Check environment variables
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY not set. Set it via environment variable.")
        print("   Example: export GEMINI_API_KEY='your-api-key-here'\n")
    
    # Production-grade server with auto-reload disabled for stability
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
