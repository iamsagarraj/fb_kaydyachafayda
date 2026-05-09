import os
import json
import random
from google import genai # Modern 2026 SDK
import facebook

# --- 1. CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

client = genai.Client(api_key=GEMINI_API_KEY)
graph = facebook.GraphAPI(access_token=FB_PAGE_TOKEN)

HISTORY_FILE = "post_history.json"
STATE_FILE = "niche_state.json"

# --- 2. LOAD DATA ---
with open(HISTORY_FILE, "r") as f: history = json.load(f)
with open(STATE_FILE, "r") as f: state = json.load(f)

# --- 3. LOGIC ---
if state["banking_count"] <= state["family_count"]:
    niche, perspective = "बँकिंग कायदा", "Technical advice on Cheque Bounce/Notices."
    state["banking_count"] += 1
else:
    niche = "कौटुंबिक कायदा"
    perspective = "Husband's Rights" if random.random() < 0.7 else "Wife's Rights"
    state["family_count"] += 1

# --- 4. GENERATE CONTENT (2026 STABLE MODELS) ---
prompt = f"Adv. Sagar Shirsat म्हणून 'कायद्याचा फायदा' साठी {niche} ({perspective}) वर पोस्ट लिहा. शुद्ध पुणेरी मराठी वापरा."

try:
    # UPDATED MODEL NAMES FOR MAY 2026
    # 'gemini-3.1-flash-lite' is the current fastest/free stable model
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", 
        contents=prompt
    )
    post_text = response.text

    # --- 5. POST TO FB ---
    graph.put_object(parent_object=FB_PAGE_ID, connection_name='feed', message=post_text)
    print("Victory! Post published.")

    # --- 6. SAVE ---
    history.append(f"{niche}: {perspective}")
    with open(HISTORY_FILE, "w") as f: json.dump(history[-50:], f)
    with open(STATE_FILE, "w") as f: json.dump(state, f)

except Exception as e:
    print(f"Error: {e}")
    # If 3.1 is busy, try the 2.5 version as a backup
    print("Attempting backup model gemini-2.5-flash...")
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    graph.put_object(parent_object=FB_PAGE_ID, connection_name='feed', message=response.text)
