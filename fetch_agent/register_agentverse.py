import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

# Set your credentials
AGENTVERSE_KEY = "eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjE0ODIwNDcsImlhdCI6MTc2MTQ3ODQ0NywiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiI5OTU1MjZmMThkMDBhN2I2NDVhNjk3N2EiLCJzY29wZSI6IiIsInN1YiI6Ijg4Y2M1YTY4NjNhZTZkYWYxYmI5OTg2MjI5Zjg4NzdmMTEwZWUyZDk1MzQ4YjBlNSJ9.aSUSmQ0vzchSSm8rLRUXtOSj4VgbqJ_3tzCSTiLQbGBiSP0yTGrcIe7gvdRN0c9jzcIkb9QCqL9_dNeusW8oraL-RqH7LtKUePe2BNNA2oEx4I2v97SpvHQb74Mi_FWexvdHZjcoPGxB7cG-2GwfPhYmrXCbPQ8Cyn06BAmNmgrK2LUNgAnRDzeAzl6T73bqpQ4BcLQdRLeqzwjvl1wLTYLJQJCUguAoEWyxw0m6HVQ0mzLjLNNb-uycK1ctdu0l3prrLuJLfgp1yhRz2uM6fpwiWGkjghTj-Rs4AmyZTfP17TikRyXBmhGxAo7a2W4Uv742AQh84FFHdHOu2_1hSA"
AGENT_SEED_PHRASE = "cryptoagent-cfo-calhacks-2025"

# Set environment variables
os.environ["AGENTVERSE_KEY"] = AGENTVERSE_KEY
os.environ["AGENT_SEED_PHRASE"] = AGENT_SEED_PHRASE

# Register the agent
register_chat_agent(
    "CryptoAgent CFO",
    "https://jussive-lonnie-gallantly.ngrok-free.dev/chat",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"],
    ),
)

print("✅ Agent registered on Agentverse!")
print("📍 Agent Address: agent1qfhnmhjwxjjs43970rqjhsw00ds054v8gt0d0735m5x6h3pttpcewy2wugj")
print("🌐 Endpoint: https://jussive-lonnie-gallantly.ngrok-free.dev/chat")
