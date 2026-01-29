from google import genai
from django.conf import settings
import time
import json
import re

print("AI_AGENT FILE LOADED")

# Initialize Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)
print("AI CLIENT INITIALIZED")


def extract_json(text):
    """
    Extract the first valid JSON object from AI output
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group())
    except Exception:
        return None


def planner_agent(user_data):
    # Ensure values exist even if keys are missing from older versions
    days = user_data.get('days', 3)
    members = user_data.get('members', 1)
    
    prompt = f"""
    CRITICAL CONSTRAINTS (DO NOT VIOLATE):
- Destination: {user_data['destination']} (STRICTLY adhere to this).
- Duration: EXACTLY {days} days.
- Travelers: {members} people.
- Budget: {user_data['budget']} INR total for {members} people.
- Style: {user_data['style']}.
- booking_link MUST be a valid clickable URL starting with https://

You are a luxury concierge system creating a highly premium travel experience.

STRICT RULES:
- Output ONLY valid JSON.
- No markdown, no explanations, no extra text.
- Calculations for stay and food MUST be realistic for {members} people.

User Info:
From: {user_data['from_city']}
To: {user_data['destination']}
Duration: {days} Days
Group Size: {members} Travelers
Budget: {user_data['budget']} INR
Notes: {user_data['notes']}

Return JSON in EXACT format:
{{
  "route": {{
    "from": "{user_data['from_city']}",
    "to": "{user_data['destination']}",
    "best_mode": "Flight / Train / Car",
    "options": [
      {{"mode": "Primary Mode", "time": "X hrs", "cost": "XXXX INR total"}}
    ]
  }},
  "hotels": [
    {{
        "name": "Luxury Hotel Name", 
        "price_per_night": "XXXX INR", 
        "image": "high quality hotel interior", 
        "booking_link": "https://www.google.com/search?q=hotel+name"
    }}
  ],
  "itinerary": [
    {{
        "day": 1, 
        "title": "Bespoke Arrival", 
        "plan": "Detailed high-end experience description",
        "photo_query": "specific landmark name at destination"
    }}
    // Generate exactly {days} day objects here
  ],
  "budget_summary": {{
    "travel": "XXXX INR",
    "stay": "XXXX INR",
    "food": "XXXX INR",
    "activities": "XXXX INR",
    "total": "XXXX INR"
  }}
}}
"""

    try:
        print(f"AI: Generating {days}-day plan for {members} travelers...")
        start_time = time.time()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'http_options': {'timeout': 30000} 
            }
        )

        elapsed = round(time.time() - start_time, 2)
        print(f"AI: Response received in {elapsed} seconds")

        raw_text = response.text
        raw_text = raw_text.encode("ascii", "ignore").decode().strip()

        data = extract_json(raw_text)

        if not data:
            print("AI ERROR: JSON parsing failed")
            return {"error": "AI returned invalid data format"}

        # Ensure the itinerary has the requested number of days
        print("AI SUCCESS: Premium plan generated")
        return data

    except Exception as e:
        print("AI ERROR:", str(e))
        return {"error": f"AI service error: {str(e)}"}