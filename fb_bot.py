import os
import json
import random
from google import genai
import facebook

# --- 1. CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

# Initialize Clients
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

# --- 4. GENERATE CONTENT ---
prompt = f"Adv. Sagar Shirsat म्हणून 'कायद्याचा फायदा' साठी {niche} ({perspective}) वर फेसबुक पोस्ट लिहा. शुद्ध पुणेरी मराठी वापरा. हेडलाईन बोल्ड करा."

print(f"Generating post for: {niche}...")

# --- 5. EXECUTION & POSTING ---
try:
    # Use 'gemini-2.0-flash' - the standard 2026 free model
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    
    if not response.text:
        raise ValueError("AI returned empty response")
        
    post_text = response.text

    # Post to FB
    graph.put_object(parent_object='me', connection_name='feed', message=post_text)
    print("Victory! Post published successfully.")

    # --- 6. SAVE STATE ---
    history.append(f"{niche}: {perspective}")
    with open(HISTORY_FILE, "w") as f: json.dump(history[-50:], f, indent=4)
    with open(STATE_FILE, "w") as f: json.dump(state, f, indent=4)

except Exception as e:
    print(f"Primary Model Failed: {e}")
    # FALLBACK: If your account is brand new, Google sometimes restricts 2.0.
    # We try 'gemini-2.0-flash-lite' as a last resort.
    print("Trying Fallback Model...")
    try:
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
        graph.put_object(parent_object='me', connection_name='feed', message=response.text)
        print("Fallback Success!")
    except Exception as e2:
        print(f"Critical Quota Failure: {e2}")
        print("ACTION REQUIRED: Go to AI Studio, create a NEW Project, and get a NEW API Key.")
        exit(1)
