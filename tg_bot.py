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

# --- 2. HELPER: TELEGRAM SENDER ---
def send_tg_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# --- 3. INITIALIZE FILES ---
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f: json.dump([], f)
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f: json.dump({"banking_count": 0, "family_count": 0}, f)

with open(HISTORY_FILE, "r") as f: history = json.load(f)
with open(STATE_FILE, "r") as f: state = json.load(f)

# --- 4. START SIGNAL ---
send_tg_message("🚀 *Tadaaaah!* Adv. Sagar's AI Bot is now generating your 3 daily posts...")

# --- 5. GENERATION LOOP (3 POSTS) ---
for i in range(1, 4):
    # Determine Niche for this specific post
    if state["banking_count"] <= state["family_count"]:
        niche, topic = "बँकिंग कायदा", "Cheque Bounce/Bank Recovery"
        state["banking_count"] += 1
    else:
        niche = "कौटुंबिक कायदा"
        topic = "Husband's Rights (Sec 9)" if random.random() < 0.7 else "Maintenance & Child Custody"
        state["family_count"] += 1

    prompt = f"Write a professional Facebook post in Marathi for Adv. Sagar Shirsat. Post #{i}. Topic: {niche} ({topic}). Use professional Puneri Marathi. Include a bold headline and 3 practical legal tips."

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
        "text": f"🚀 *Tadaaaah! Post generated:*\n\n{article}",
        "parse_mode": "Markdown"
    }
    
    response = requests.post(tg_url, data=payload)
    
    # DEBUG LOGS - This will show us the truth!
    print(f"Telegram Response Status: {response.status_code}")
    print(f"Telegram Response Body: {response.text}")
    
    if response.status_code != 200:
        print("❌ Telegram failed to send the message!")
    else:
        print("✅ Telegram says it sent the message successfully.")
        # Save to history
        history.append(f"Post {i} - {niche}: {topic}")

    except Exception as e:
        send_tg_message(f"❌ Error generating Post #{i}: {e}")

# --- 6. SAVE UPDATED STATE ---
with open(HISTORY_FILE, "w") as f: json.dump(history[-100:], f, indent=4)
with open(STATE_FILE, "w") as f: json.dump(state, f, indent=4)

print("All 3 posts sent to Telegram successfully!")
