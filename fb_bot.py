import os
from google import genai # Use the new library

# Setup API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Inside your generation logic, replace the old response code with this:
response = client.models.generate_content(
    model="gemini-2.0-flash", # Use the 2.0 version (standard in 2026)
    contents=prompt
)
post_text = response.text
