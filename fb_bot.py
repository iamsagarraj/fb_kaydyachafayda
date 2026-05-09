import os
import json
import random
import facebook
from huggingface_hub import InferenceClient

# --- 1. CONFIGURATION ---
HF_TOKEN = os.getenv("HF_TOKEN")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

# Llama-3-8B is excellent for Marathi and has a reliable free API
client = InferenceClient(token=HF_TOKEN)
graph = facebook.GraphAPI(access_token=FB_PAGE_TOKEN)

HISTORY_FILE = "post_history.json"
STATE_FILE = "niche_state.json"

# --- 2. LOAD DATA ---
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f: json.dump([], f)
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f: json.dump({"banking_count": 0, "family_count": 0}, f)

with open(HISTORY_FILE, "r") as f: history = json.load(f)
with open(STATE_FILE, "r") as f: state = json.load(f)

# --- 3. LOGIC (50/50 Niche & 70/30 Perspective) ---
if state["banking_count"] <= state["family_count"]:
    niche, topic = "बँकिंग कायदा", "Cheque Bounce and Bank Notices"
    state["banking_count"] += 1
else:
    niche = "कौटुंबिक कायदा"
    topic = "Husband's Rights (Section 9/498A)" if random.random() < 0.7 else "Wife's Rights"
    state["family_count"] += 1

# --- 4. GENERATE CONTENT ---
prompt = f"Write a professional Facebook post in Marathi for Advocate Sagar Shirsat. Topic: {niche} ({topic}). Use a professional Puneri Marathi tone. Include a catchy headline and legal advice."

print(f"Generating via Hugging Face for: {niche}...")

try:
    # Inference API call
    output = client.chat_completion(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    post_text = output.choices[0].message.content

    # --- 5. POST TO FB ---
    # Using 'me' is the most reliable parent_object for Page Tokens
    graph.put_object(parent_object='me', connection_name='feed', message=post_text)
    print("Victory! Post published via Hugging Face.")

    # --- 6. SAVE STATE ---
    history.append(f"{niche}: {topic}")
    with open(HISTORY_FILE, "w") as f: json.dump(history[-50:], f, indent=4)
    with open(STATE_FILE, "w") as f: json.dump(state, f, indent=4)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
