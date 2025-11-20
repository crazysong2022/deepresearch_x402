from fastapi import FastAPI, Request, Depends
from openai import OpenAI
from x402.fastapi import require_payment_dependency  # ← 重点：新方式
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

class Query(BaseModel):
    question: str

# 正确方式：定义一个依赖
async def payment_dependency(request: Request):
    await require_payment_dependency(
        request,
        price="0.03",
        pay_to_address=os.getenv("RECEIVER_WALLET"),
        network="base"
    )

@app.post("/research")
async def deep_research(q: Query, _: None = Depends(payment_dependency)):  # ← 关键在这里
    print("Payment verified! Calling Perplexity...")

    resp = client.chat.completions.create(
        model="sonar-large-online",
        messages=[{"role": "user", "content": q.question}],
        max_tokens=4000
    )
    answer = resp.choices[0].message.content
    return {"answer": answer}

# 以下所有接口免费
@app.get("/")
async def root():
    return {"message": "x402 DeepResearch API ready – POST /research with X-PAYMENT"}

@app.get("/health")
async def health():
    return {"status": "ok"}