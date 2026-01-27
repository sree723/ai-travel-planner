def safe_print(text):
    try:
        print(str(text).encode("utf-8", "ignore").decode())
    except Exception:
        print("[AI OUTPUT: UNPRINTABLE DATA]")
def planner_agent(user_data):
    prompt = f"""
You are a professional travel planning system.

STRICT RULES:
- Output ONLY valid JSON
- Use ONLY English characters
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

        # -------- SAFE EXTRACTION (NO PRINTING RAW OBJECTS) --------
        try:
            raw_text = response.candidates[0].content.parts[0].text
        except Exception:
            return {"error": "AI returned empty response"}

        # -------- SANITIZE BEFORE USING --------
        raw_text = raw_text.encode("ascii", "ignore").decode().strip()

        data = extract_json(raw_text)

        if not data:
            return {"error": "AI returned invalid data format"}

        return data

    except Exception as e:
        print(f"AI ERROR: {e}")
        return {"error": "AI service is currently unavailable"}