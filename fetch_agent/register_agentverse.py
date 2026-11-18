import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

from dotenv import load_dotenv

load_dotenv()

# Credentials come from the environment (see .env.example). Never commit them.
AGENTVERSE_KEY = os.environ.get("AGENTVERSE_KEY")
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED", "cryptoagent-cfo-calhacks-2025")
PUBLIC_URL = os.environ.get("PUBLIC_URL")  # public HTTPS URL of the running agent, e.g. an ngrok tunnel

if not AGENTVERSE_KEY or not PUBLIC_URL:
    raise SystemExit("Set AGENTVERSE_KEY and PUBLIC_URL in .env first (see README).")

# Register the agent
register_chat_agent(
    "CryptoAgent CFO",
    f"{PUBLIC_URL.rstrip('/')}/chat",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=AGENTVERSE_KEY,
        agent_seed_phrase=AGENT_SEED_PHRASE,
    ),
)

print("✅ Agent registered on Agentverse!")
print(f"🌐 Endpoint: {PUBLIC_URL.rstrip('/')}/chat")
