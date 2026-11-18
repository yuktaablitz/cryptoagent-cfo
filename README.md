# CryptoAgent CFO

**CalHacks 12.0 · 3rd place.** A natural-language crypto "CFO" for students: describe your situation in plain English
("I have $1000 in crypto and need $400 for rent, I'm risk-averse") and get a liquidation plan that says which coins to
sell, how much of each, and why.

## How it works

```
User (web page / ASI:One chat)
   │  plain-English request
   ▼
Postman Flows  ── AI Agent block extracts runway, expense and risk tolerance
   │            ── fetches live prices from the Gemini exchange API
   ▼
Fetch.ai uAgent + FastAPI  (fetch_agent/agent.py)
   │  risk-aware liquidation strategy
   ▼
Plan: assets to sell, amounts, rationale, warnings
```

- **Conservative** (`low`): sells the most volatile assets first (SOL → ETH → BTC) to keep the stable holdings.
- **Aggressive** (`high`): sells the stable assets first to keep the high-growth ones.
- **Balanced** (`medium`): sells the smallest positions first.
- Warns when the portfolio cannot cover the expense or when more than 80% of it would be sold.

The orchestration (prompt parsing with the Postman AI Agent block and the Gemini price lookup) lives in a Postman Flow,
which is not stored in this repo. The agent in this repo also parses the prompt itself, so it runs on its own.

## Repo layout

```
fetch_agent/agent.py               FastAPI app + Fetch.ai uAgent: /, /plan, /chat, /health
fetch_agent/mock_portfolio.json    demo portfolio (BTC, ETH, SOL; $1,500 total)
fetch_agent/register_agentverse.py registers the agent's /chat endpoint on Agentverse (ASI:One chat protocol)
index.html                         single-page web UI
```

## Run it locally

Requires Python 3.10+.

```bash
git clone https://github.com/yuktaablitz/cryptoagent-cfo.git
cd cryptoagent-cfo
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
cd fetch_agent && python agent.py                       # serves http://localhost:8080
```

Try it:

```bash
curl -s localhost:8080/health
curl -s localhost:8080/plan -H 'Content-Type: application/json' \
  -d '{"runway_usd":1000,"required_expense_usd":400,"risk_tolerance":"low"}'
curl -s localhost:8080/ -H 'Content-Type: application/json' \
  -d '{"user_prompt":"I have $1000 and need $400 for rent, I want to be conservative"}'
curl -s localhost:8080/chat -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"I have $500 and need $300, risk-averse"}]}'
```

Open `index.html` in a browser for the UI. It calls `http://localhost:8080` by default; to point it at a deployed
agent, open `index.html?api=https://your-agent-url`.

Pass your own holdings with `portfolio_override` in the request body (same shape as `mock_portfolio.json`).

## Publish to Agentverse / ASI:One (optional)

1. Expose the agent publicly, for example `ngrok http 8080`.
2. Put your Agentverse API key and the public URL in `.env` (`AGENTVERSE_KEY`, `PUBLIC_URL`).
3. `python fetch_agent/register_agentverse.py`

## Tech stack

Python, FastAPI, Pydantic, Fetch.ai uAgents / Agentverse, Postman Flows (AI Agent block), Gemini exchange API, HTML/CSS/JS.

*Not financial advice. Demo portfolio only.*
