from fastapi import FastAPI
from openai import OpenAI
from x402.fastapi.middleware import require_payment  # ← Correct import
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="DeepResearch x402 — Unlimited Perplexity Pro",
 description="Pay 0.03 USDC per deep research query — built for AI agents",
 version="1.0"
)

# Perplexity client
client = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)

# ← THIS IS THE OFFICIAL, WORKING WAY (no facilitator_url needed)
app.middleware("http")(
    require_payment(
        price="0.03",                    # Exact string: "0.03" means 0.03 USDC
        pay_to_address=os.getenv("RECEIVER_WALLET"),
        network="base"                   # "base" for mainnet, "base-sepolia" for testing
        # The public facilitator is used automatically — zero extra config!
    )
)

class Query(BaseModel):
    question: str

@app.post("/research")
async def deep_research(q: Query):
    response = client.chat.completions.create(
        model="sonar-large-online",
        messages=[{"role": "user", "content": q.question}],
        max_tokens=4000
    )
    return {
        "answer": response.choices[0].message.content,
        "model": "sonar-large-online",
        "cost": "0.03 USDC"
    }

@app.get("/")
async def root():
    return {"message": "DeepResearch x402 API live — AI agents welcome!"}