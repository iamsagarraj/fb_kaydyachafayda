import os
import json
import random
import requests
from huggingface_hub import InferenceClient

# --- 1. CONFIGURATION ---
HF_TOKEN = os.getenv("HF_TOKEN")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = InferenceClient(token=HF_TOKEN)

HISTORY_FILE = "post_history.json"
STATE_FILE = "niche_state.json"

# --- 2. LOAD DATA ---
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f: json.dump([], f)
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f: json.dump({"banking_count": 0, "family_count": 0}, f)

with open(HISTORY_FILE, "r") as f: history = json.load(f)
with open(STATE_FILE, "r") as f: state = json.load(f)

# --- 3. LOGIC ---
if state["banking_count"] <= state["family_count"]:
    niche, topic = "बँकिंग कायदा", "Cheque Bounce and Bank Notices"
    state["banking_count"] += 1
else:
    niche = "कौटुंबिक कायदा"
    topic = "Husband's Rights" if random.random() < 0.7 else "Wife's Rights"
    state["family_count"] += 1

# --- 4. GENERATE CONTENT ---
prompt = f"Write a professional Facebook post in Marathi for Adv. Sagar Shirsat. Topic: {niche} ({topic}). Use professional Puneri Marathi. Include a bold headline and legal tips."

print(f"Generating for: {niche}...")

try:
    output = client.chat_completion(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    article = output.choices[0].message.content

    # --- 5. SEND TO TELEGRAM ---
    tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": f"📢 *Today's Post for Kaydyacha Fayda* 📢\n\n{article}",
        "parse_mode": "Markdown"
    }
    requests.post(tg_url, data=payload)
    print("Article sent to Telegram!")

    # --- 6. SAVE STATE ---
    history.append(f"{niche}: {topic}")
    with open(HISTORY_FILE, "w") as f: json.dump(history[-50:], f, indent=4)
    with open(STATE_FILE, "w") as f: json.dump(state, f, indent=4)

except Exception as e:
    print(f"Error: {e}")
