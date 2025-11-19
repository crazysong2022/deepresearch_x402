from fastapi import FastAPI, Request, Response
from openai import OpenAI
from x402.fastapi import X402Negotiator
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="DeepResearch x402 – Unlimited Perplexity Pro",
    description="0.03 USDC per deep research query – built for AI agents",
    version="1.0"
)

client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"), base_url="https://api.perplexity.ai")

# ← This is the correct negotiator that sends proper lowercase headers
negotiator = X402Negotiator(
    default_price="0.03",                     # 0.03 USDC
    pay_to_address=os.getenv("RECEIVER_WALLET"),
    network="base"
)

class Query(BaseModel):
    question: str

@app.post("/research")
async def deep_research(request: Request, q: Query):
    # This line triggers payment ONLY for this endpoint and sends correct headers
    await negotiator.negotiate(request)
    
    resp = client.chat.completions.create(
        model="sonar-large-online",
        messages=[{"role": "user", "content": q.question}],
        max_tokens=4000
    )
    return {"answer": resp.choices[0].message.content}

@app.get("/")
async def root():
    return {"message": "DeepResearch x402 API – POST /research to use (0.03 USDC)"}