from fastapi import FastAPI, Request, Response
from openai import OpenAI
from x402.fastapi.middleware import require_payment
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

# Global middleware – applies to all endpoints (including /)
app.middleware("http")(
    require_payment(
        price="0.03",
        pay_to_address=os.getenv("RECEIVER_WALLET"),
        network="base"
    )
)

class Query(BaseModel):
    question: str

@app.post("/research")
async def deep_research(q: Query):
    resp = client.chat.completions.create(
        model="sonar-large-online",
        messages=[{"role": "user", "content": q.question}],
        max_tokens=4000
    )
    return {"answer": resp.choices[0].message.content}

@app.get("/")
async def root():
    return {"message": "DeepResearch x402 API – POST /research with payment"}