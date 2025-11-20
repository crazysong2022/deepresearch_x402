from fastapi import FastAPI, Request
from openai import OpenAI
from x402.fastapi.middleware import require_payment   # 装饰器方式
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

# ┌─────────────────────────────────────────────────────────────┐
# │  重点：只在 /research 上加支付要求，其他路径免费开放       │
# └─────────────────────────────────────────────────────────────┘
@app.post("/research")
@require_payment(price="0.03", pay_to_address=os.getenv("RECEIVER_WALLET"), network="base")
async def deep_research(q: Query, request: Request):
    print("Payment verified! Calling Perplexity...")

    resp = client.chat.completions.create(
        model="sonar-large-online",
        messages=[{"role": "user", "content": q.question}],
        max_tokens=4000
    )
    answer = resp.choices[0].message.content
    return {"answer": answer}

# 以下所有路径都不需要支付
@app.get("/")
async def root():
    return {"message": "DeepResearch x402 API – POST /research with X-PAYMENT header"}

@app.get("/expected-format")
async def expected_format():
    return {
        "note": "Use the latest signed payment format (nonce + signature)",
        "docs": "https://github.com/x402-protocol/fastapi-middleware#signed-payment-proof"
    }

@app.post("/debug-payment")
async def debug_payment(request: Request):
    header = request.headers.get("X-PAYMENT")
    return {"received_X_PAYMENT": header[:100] + "..." if header else None}