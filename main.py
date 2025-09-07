from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(title="Marketplace Agents")


# app = FastAPI(title="Marketplace Agents")

# Allow frontend (localhost) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"] if serving HTML via Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Request Schemas ---------
class Product(BaseModel):
    title: str
    category: str
    condition: str
    age_months: int
    asking_price: int

class Message(BaseModel):
    text: str


# --------- Helper: Call Groq API ---------
def call_groq(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",  #  Recommended active model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for marketplace agents."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )
    result = response.json()
    try:
        return result["choices"][0]["message"]["content"]
    except Exception:
        print("❌ Groq API Response:", result)
        return "Error from Groq API"





# --------- Price Suggestor Agent ---------
@app.post("/negotiate")
def negotiate(product: Product):
    # Basic rule-based price estimation
    depreciation_rate = 0.05
    base_price = product.asking_price
    estimated_value = base_price * ((1 - depreciation_rate) ** (product.age_months / 12))

    if product.condition == "Like New":
        estimated_value *= 1.1
    elif product.condition == "Fair":
        estimated_value *= 0.8

    suggested_range = {
        "min": round(estimated_value * 0.9),
        "max": round(estimated_value * 1.1)
    }

    # Ask Groq for reasoning
    prompt = (
        f"Suggest a fair price for a {product.condition} {product.title} "
        f"({product.category}), age {product.age_months} months, asking ₹{product.asking_price}. "
        f"Give reasoning in 2-3 sentences."
    )
    reasoning = call_groq(prompt)

    return {
        "suggested_price_range": suggested_range,
        "reasoning": reasoning
    }


# --------- Moderation Agent ---------
@app.post("/moderate")
def moderate(message: Message):
    text = message.text

    # Simple rule-based detection
    status = "Safe"
    reason = "Message is clean."

    if any(word in text.lower() for word in ["abuse", "scam", "fraud"]):
        status = "Abusive/Spam"
        reason = "Contains suspicious or abusive words."
    elif any(char.isdigit() for char in text) and ("+" in text or "@" in text):
        status = "Sensitive"
        reason = "Message contains phone number or email."

    # Ask Groq for AI moderation reasoning
    prompt = (
        f"Classify this message for marketplace safety:\n\n"
        f"Message: \"{text}\"\n\n"
        f"Return Safe / Abusive-Spam / Sensitive and explain in one line."
    )
    ai_reasoning = call_groq(prompt)

    return {
        "status": status,
        "reason": reason,
        "ai_reasoning": ai_reasoning
    }
