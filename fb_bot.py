import facebook
from google import genai
import os

# ================= CONFIGURATION =================
# Replace these with your actual credentials
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
FB_PAGE_ACCESS_TOKEN = "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN"
FB_PAGE_ID = "YOUR_PAGE_ID"

# The topic you want the AI to write about today
POST_TOPIC = "Importance of Technical Analysis in Stock Trading for 2026"
# =================================================

def generate_ai_content(topic):
    """Generates professional post content using Gemini 3 Flash."""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        Write a professional and engaging Facebook post about: {topic}.
        Include:
        1. A catchy headline.
        2. 3 key bullet points.
        3. Relevant hashtags.
        4. A call to action.
        Keep the tone informative and encouraging.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Latest stable model for 2026
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

def post_to_facebook(message):
    """Publishes the message to the specified Facebook Page."""
    try:
        # Initialize the Graph API
        graph = facebook.GraphAPI(access_token=FB_PAGE_ACCESS_TOKEN)
        
        # Post to the Page's feed
        result = graph.put_object(
            parent_object=FB_PAGE_ID, 
            connection_name="feed", 
            message=message
        )
        
        print(f"Successfully posted! Post ID: {result['id']}")
    except facebook.GraphAPIError as e:
        print(f"Facebook Graph API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    print("--- Starting FB Bot ---")
    
    # 1. Generate Content
    print("Generating content with Gemini AI...")
    content = generate_ai_content(POST_TOPIC)
    
    if content:
        print("\nGenerated Content Preview:")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        # 2. Publish to Facebook
        confirm = input("\nDo you want to publish this to Facebook? (y/n): ")
        if confirm.lower() == 'y':
            post_to_facebook(content)
        else:
            print("Post cancelled.")
    else:
        print("Failed to generate content. Check your API key.")

if __name__ == "__main__":
    main()
