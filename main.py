from fastapi import FastAPI, Request, Response
from openai import OpenAI
from x402.fastapi.middleware import require_payment
from pydantic import BaseModel
import os
import base64
import json
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
async def deep_research(q: Query, request: Request):
    # 添加详细的调试信息
    payment_header = request.headers.get("X-PAYMENT")
    print(f"🔍 Received X-PAYMENT header: {payment_header}")
    
    if payment_header:
        print(f"🔍 Header length: {len(payment_header)}")
        print(f"🔍 Header type: {type(payment_header)}")
        # 尝试解码以查看内容
        try:
            decoded = base64.b64decode(payment_header)
            print(f"🔍 Base64 decoded: {decoded[:100]}...")  # 只显示前100个字符
        except Exception as e:
            print(f"🔍 Base64 decode failed: {e}")
    
    resp = client.chat.completions.create(
        model="sonar-large-online",
        messages=[{"role": "user", "content": q.question}],
        max_tokens=4000
    )
    return {"answer": resp.choices[0].message.content}

@app.get("/")
async def root():
    return {"message": "DeepResearch x402 API – POST /research with payment"}

# 添加一个不要求支付的调试端点
@app.post("/debug-payment")
async def debug_payment(request: Request):
    payment_header = request.headers.get("X-PAYMENT")
    debug_info = {
        "received_x_payment": payment_header,
        "header_length": len(payment_header) if payment_header else 0,
    }
    
    if payment_header:
        # 尝试分析头部内容
        try:
            # 尝试Base64解码
            decoded = base64.b64decode(payment_header)
            debug_info["base64_decoded_length"] = len(decoded)
            debug_info["base64_decoded_preview"] = decoded[:50].hex()  # 十六进制预览
        except Exception as e:
            debug_info["base64_decode_error"] = str(e)
        
        # 尝试JSON解析（如果是Base64解码后的内容）
        try:
            if 'decoded' in locals():
                json_data = json.loads(decoded)
                debug_info["json_content"] = json_data
        except:
            debug_info["json_decode_failed"] = True
    
    return debug_info

# 添加一个示例端点显示期望的格式
@app.get("/expected-format")
async def expected_format():
    """显示x402中间件期望的支付头格式"""
    example_data = {
        "scheme": "exact",
        "network": "base",
        "txHash": "0x1234567890abcdef...",
        "amount": "30000",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    }
    
    example_json = json.dumps(example_data)
    example_base64 = base64.b64encode(example_json.encode()).decode()
    
    return {
        "expected_format": "Base64 encoded JSON",
        "example_json": example_data,
        "example_base64": example_base64,
        "usage_note": "Set X-PAYMENT header to the base64 string"
    }