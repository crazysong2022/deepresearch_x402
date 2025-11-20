from fastapi import FastAPI, Request
from openai import OpenAI
from x402.fastapi.middleware import require_payment  # ← 保持这个导入
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
# │ 关键修复：恢复全局 middleware，但只对 /research 生效       │
# │ 用依赖注入方式排除其他路径（这样调试端点免费）             │
# └─────────────────────────────────────────────────────────────┘

from fastapi import Depends

async def skip_payment_for_non_research(request: Request, call_next):
    if request.url.path != "/research":
        # 非 /research 路径直接放行（免费）
        return await call_next(request)
    
    # /research 路径才走支付验证
    middleware = require_payment(
        price="0.03",
        pay_to_address=os.getenv("RECEIVER_WALLET"),
        network="base"
    )
    return await middleware(request, call_next)

app.middleware("http")(skip_payment_for_non_research)

# 现在 /research 正常走支付验证
@app.post("/research")
async def deep_research(q: Query, request: Request):
    print("Payment verified successfully! Calling Perplexity...")

    resp = client.chat.completions.create(
        model="sonar-large-online",
        messages=[{"role": "user", "content": q.question}],
        max_tokens=4000
    )
    answer = resp.choices[0].message.content
    return {"answer": answer}

# 以下所有路径免费
@app.get("/")
async def root():
    return {"message": "DeepResearch x402 API – POST /research with X-PAYMENT"}

@app.post("/debug-payment")
async def debug_payment(request: Request):
    header = request.headers.get("X-PAYMENT")
    return {"received": bool(header), "preview": header[:100] if header else None}

@app.get("/expected-format")
async def expected_format():
    return {"note": "Use signed payment proof with nonce + signature"}