from google import genai
from django.conf import settings
import time
import json
import re

# Create Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def extract_json(text):
    """
    Extracts the first valid JSON object found in a string.
    Protects against AI adding explanations or extra text.
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group())
    except Exception:
        return None


def planner_agent(user_data):
    prompt = f"""
You are a professional travel planning system.

STRICT RULES:
- Output ONLY valid JSON
- No markdown
- No explanations
- No extra text

User Info:
From City: {user_data['from_city']}
Destination: {user_data['destination']}
Budget: {user_data['budget']} INR
Style: {user_data['style']}
Notes: {user_data['notes']}

Return JSON in EXACT format:
{{
  "route": {{
    "from": "{user_data['from_city']}",
    "to": "{user_data['destination']}",
    "best_mode": "Flight / Train / Car / Bike",
    "options": [
      {{"mode": "Flight", "time": "X hrs", "cost": "XXXX INR"}},
      {{"mode": "Train", "time": "X hrs", "cost": "XXXX INR"}},
      {{"mode": "Car", "time": "X hrs", "cost": "XXXX INR"}}
    ]
  }},
  "hotels": [
    {{"name": "Hotel name", "price_per_night": "XXXX INR", "image": "hotel resort", "booking_link": "https://www.google.com/travel/hotels"}},
    {{"name": "Hotel name", "price_per_night": "XXXX INR", "image": "luxury hotel", "booking_link": "https://www.google.com/travel/hotels"}}
  ],
  "itinerary": [
    {{"day": 1, "title": "Arrival & Local Sightseeing", "plan": "Details"}},
    {{"day": 2, "title": "Main Attractions", "plan": "Details"}},
    {{"day": 3, "title": "Leisure & Return", "plan": "Details"}}
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
        print("AI: Sending request to Gemini...")
        start_time = time.time()

        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        elapsed = round(time.time() - start_time, 2)
        print(f"AI: Response received in {elapsed} seconds")

        raw_text = response.text.strip()
        print("AI RAW OUTPUT:\n", raw_text)

        data = extract_json(raw_text)

        if not data:
            return {"error": "AI returned invalid data format"}

        return data

    except Exception as e:
        print("AI ERROR:", str(e))
        return {"error": "AI service is currently unavailable"}
