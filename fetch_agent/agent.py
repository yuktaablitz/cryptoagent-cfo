from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uagents import Agent, Context
from typing import Optional, List
import os, json, re
from dotenv import load_dotenv

load_dotenv()

AGENT_SEED = os.environ.get("AGENT_SEED", "cryptoagent-cfo-calhacks-2025")
AGENT_PORT = int(os.environ.get("AGENT_PORT", "8080"))

agent = Agent(name="crypto_cfo_agent", seed=AGENT_SEED, port=8000, endpoint=[f"http://localhost:8000/submit"])

app = FastAPI(title="CryptoAgent CFO", description="AI-powered crypto portfolio liquidation advisor", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class AssetAction(BaseModel):
    symbol: str
    sell_usd: float
    sell_fraction: float
    reason: str

class PlanRequest(BaseModel):
    runway_usd: float
    required_expense_usd: float
    risk_tolerance: str = "medium"
    portfolio_override: Optional[dict] = None

class PlanResponse(BaseModel):
    liquidation_plan: List[AssetAction]
    keep_holdings: List[dict]
    total_freed_usd: float
    remaining_portfolio_usd: float
    rationale: str
    warnings: List[str]
    agent_address: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

def load_mock_portfolio():
    portfolio_path = os.path.join(os.path.dirname(__file__), "mock_portfolio.json")
    with open(portfolio_path) as f:
        return json.load(f)

def parse_prompt(text: str):
    nums = [float(x) for x in re.findall(r'\$?(\d+(?:\.\d+)?)', text)]
    runway = nums[0] if nums else 1000
    expense = nums[1] if len(nums) > 1 else 500
    t = text.lower()
    if any(w in t for w in ["conservative", "risk-averse", "safe", "careful", "low"]): risk = "low"
    elif any(w in t for w in ["aggressive", "risky", "growth", "yolo", "high"]): risk = "high"
    else: risk = "medium"
    return runway, expense, risk

def calculate_liquidation_plan(runway, expense, portfolio, risk):
    holdings = portfolio["holdings"].copy()
    volatility_map = {"BTC": 1, "ETH": 2, "SOL": 3}
    if risk == "low": holdings.sort(key=lambda h: volatility_map.get(h["symbol"], 99), reverse=True)
    elif risk == "high": holdings.sort(key=lambda h: volatility_map.get(h["symbol"], 99))
    else: holdings.sort(key=lambda h: h["usd_value"])
    
    to_sell, remaining, need, total_freed = [], [], float(expense), 0.0
    for h in holdings:
        if need <= 0:
            remaining.append(h)
            continue
        take_usd = min(h["usd_value"], need)
        sell_fraction = round(take_usd / h["usd_value"], 4) if h["usd_value"] > 0 else 0
        reason = "Higher volatility - preserving stable assets" if risk == "low" else "Lower volatility - preserving growth potential" if risk == "high" else "Balanced liquidation strategy"
        to_sell.append(AssetAction(symbol=h["symbol"], sell_usd=round(take_usd, 2), sell_fraction=sell_fraction, reason=reason))
        total_freed += take_usd
        need -= take_usd
        remain_val = h["usd_value"] - take_usd
        if remain_val > 1:
            remaining.append({"symbol": h["symbol"], "amount": round(h["amount"] * (1 - sell_fraction), 8), "usd_value": round(remain_val, 2)})
    
    rationale = f"Parsed runway=${runway:.2f}, expense=${expense:.2f}, risk='{risk}'. Generated liquidation plan to cover ${expense:.2f} with '{risk}' risk tolerance. "
    if risk == "low": rationale += "Sold volatile assets (SOL, ETH) first to preserve stable BTC."
    elif risk == "high": rationale += "Sold stable BTC first to preserve growth assets (SOL, ETH)."
    else: rationale += "Used balanced proportional approach."
    
    warnings = []
    if need > 0: warnings.append(f"Insufficient funds: short by ${need:.2f}")
    if total_freed > portfolio["total_usd"] * 0.8: warnings.append("Liquidating >80% of portfolio")
    
    remaining_value = sum(h.get("usd_value", 0) for h in remaining)
    return to_sell, remaining, total_freed, remaining_value, rationale, warnings

@app.get("/")
async def root():
    return {"service": "CryptoAgent CFO", "status": "active", "agent_address": agent.address}

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_address": agent.address}

@app.post("/")
async def root_post(request: Request):
    try:
        body = await request.json()
    except:
        body = {}
    
    if "user_prompt" in body or "prompt" in body:
        text = body.get("user_prompt") or body.get("prompt") or ""
        runway, expense, risk = parse_prompt(text)
    else:
        runway = body.get("runway_usd", 1000)
        expense = body.get("required_expense_usd", 500)
        risk = body.get("risk_tolerance", "medium")
    
    portfolio = body.get("portfolio_override") or load_mock_portfolio()
    to_sell, remaining, total_freed, remaining_value, rationale, warnings = calculate_liquidation_plan(runway, expense, portfolio, risk)
    
    return {
        "liquidation_plan": [a.dict() for a in to_sell],
        "keep_holdings": remaining,
        "total_freed_usd": round(total_freed, 2),
        "remaining_portfolio_usd": round(remaining_value, 2),
        "rationale": rationale,
        "warnings": warnings,
        "agent_address": agent.address
    }

@app.post("/plan")
async def plan(request: Request):
    return await root_post(request)

@app.post("/chat")
async def chat(req: ChatRequest):
    user_text = next((m.content for m in req.messages if m.role == "user"), "")
    runway, expense, risk = parse_prompt(user_text)
    portfolio = load_mock_portfolio()
    to_sell, remaining, total_freed, remaining_value, rationale, warnings = calculate_liquidation_plan(runway, expense, portfolio, risk)
    
    actions = "\n".join([f"Sell ${a.sell_usd} of {a.symbol} ({a.sell_fraction*100:.1f}%) - {a.reason}" for a in to_sell])
    warns = "\n".join(warnings) if warnings else "No warnings."
    msg = f"""Liquidation Plan to Cover ${expense}

Actions:
{actions}

Remaining: ${remaining_value:.2f}
Rationale: {rationale}
Warnings: {warns}
Agent: {agent.address}"""
    
    return {"messages": [{"role": "assistant", "content": msg}], "data": {"liquidation_plan": [a.dict() for a in to_sell], "keep_holdings": remaining, "total_freed_usd": round(total_freed, 2), "remaining_portfolio_usd": round(remaining_value, 2), "rationale": rationale, "warnings": warnings, "agent_address": agent.address}}

@agent.on_event("startup")
async def on_start(ctx: Context):
    ctx.logger.info(f"Agent started: {agent.address}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
