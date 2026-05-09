import os
import json
import random
from google import genai
import facebook

# --- 1. CONFIGURATION & API SETUP ---
# These secrets must be added to your GitHub Repository Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

client = genai.Client(api_key=GEMINI_API_KEY)
graph = facebook.GraphAPI(access_token=FB_PAGE_TOKEN)

HISTORY_FILE = "post_history.json"
STATE_FILE = "niche_state.json"

# --- 2. INITIALIZE FILES IF THEY DON'T EXIST ---
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f:
        json.dump({"banking_count": 0, "family_count": 0}, f)

# Load existing data
with open(HISTORY_FILE, "r") as f:
    history = json.load(f)
with open(STATE_FILE, "r") as f:
    state = json.load(f)

# --- 3. DECISION LOGIC (50/50 NICHE & 70/30 HUSBAND/WIFE) ---
if state["banking_count"] <= state["family_count"]:
    niche = "बँकिंग कायदा (Banking Law)"
    sub_topic = "Cheque Bounce, Loan Recovery, or Bank Notices"
    perspective = "Technical and Solution-oriented advice for common citizens."
    state["banking_count"] += 1
else:
    niche = "कौटुंबिक कायदा (Family Law)"
    # 70% chance for Husband's issues, 30% for Wife's
    if random.random() < 0.70:
        perspective = "Husband's Rights (Section 9, Alimony, Child Custody, or 498A Defense)"
    else:
        perspective = "Wife's Rights (Maintenance, Stridhan, or Domestic Violence laws)"
    sub_topic = "Family disputes and legal remedies"
    state["family_count"] += 1

# --- 4. GENERATE CONTENT WITH GEMINI 2.0 ---
# History context to avoid repeats
past_topics = ", ".join(history[-15:])

prompt = f"""
You are Adv. Sagar Shirsat, a professional and respected advocate from Ahilyanagar.
Write a Facebook post for your page 'Kaydyacha Fayda'.

TOPIC: {niche}
FOCUS: {perspective}
TONE: Shuddh Puneri Marathi (Authoritative, Helpful, Professional).

STRUCTURE:
1. A bold, catchy headline in Marathi.
2. A short paragraph (4-5 lines) explaining a common legal problem.
3. A clear solution or legal advice (6-8 lines) in simple Marathi.
4. End with an engaging question for the readers to comment on.

IMPORTANT: Do not repeat these previous topics: {past_topics}.
The language should be 'Humanly' and not look like an AI translation.
"""

print(f"Generating post for: {niche} ({perspective})...")

response = client.models.generate_content(
    model="gemini-2.0-flash", 
    contents=prompt
)
post_text = response.text

# --- 5. POST TO FACEBOOK ---
try:
    graph.put_object(parent_object=FB_PAGE_ID, connection_name='feed', message=post_text)
    print("Post successfully published to Facebook!")
    
    # --- 6. UPDATE HISTORY & STATE ---
    # Store a summary of the topic to prevent future repeats
    history.append(f"{niche}: {perspective[:30]}")
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-100:], f, indent=4) # Keep last 100 posts
        
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
        
except Exception as e:
    print(f"Error posting to Facebook: {e}")
    exit(1)
