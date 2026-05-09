import os
import json
import random
import google.generativeai as genai
import facebook

# 1. Setup APIs (Secrets from GitHub)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
fb_token = os.getenv("FB_PAGE_TOKEN")
fb_page_id = os.getenv("FB_PAGE_ID")
graph = facebook.GraphAPI(access_token=fb_token)

# 2. Load History and State
HISTORY_FILE = "post_history.json"
STATE_FILE = "niche_state.json"

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f: json.dump([], f)
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f: json.dump({"banking_count": 0, "family_count": 0}, f)

with open(HISTORY_FILE, "r") as f: history = json.load(f)
with open(STATE_FILE, "r") as f: state = json.load(f)

# 3. Decision Logic (50/50 Niche & 70/30 Gender)
if state["banking_count"] <= state["family_count"]:
    niche = "Banking Law (Cheque Bounce, Recovery, Loan rights)"
    perspective = "Technical and Solution-oriented"
    state["banking_count"] += 1
else:
    niche = "Family Law (Divorce, Maintenance, Custody)"
    perspective = "Husband's Rights/Problems" if random.random() < 0.7 else "Wife's Rights/Problems"
    state["family_count"] += 1

# 4. Generate Content with Gemini
model = genai.GenerativeModel('gemini-1.5-flash')
prompt = f"""
You are Adv. Sagar Shirsat, a professional advocate from Ahilyanagar.
Write a Facebook post for 'Kaydyacha Fayda' in Puneri Marathi.
Topic: {niche} focusing on {perspective}.
Format:
- Bold Headline
- Common legal scenario (4-5 lines)
- Legal solution/remedy (6-8 lines)
- End with a question for readers.

Avoid repeating these recent topics: {history[-10:]}
"""

response = model.generate_content(prompt)
post_text = response.text

# 5. Post to Facebook
graph.put_object(parent_object=fb_page_id, connection_name='feed', message=post_text)

# 6. Save State
history.append(niche + " - " + perspective)
with open(HISTORY_FILE, "w") as f: json.dump(history[-100:], f)
with open(STATE_FILE, "w") as f: json.dump(state, f)
