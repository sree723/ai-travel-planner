from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, date
import urllib.parse

from .ai_agent import planner_agent
from .free_images import get_place_image
from .trust_engine import evaluate_plan

from .models import (
    Trip,
    TripMemory,
    HiddenPlace,
    TripPlan
)

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def hotel_search_link(hotel_name, destination):
    query = f"{hotel_name} {destination} official booking"
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)

# -------------------
# HOME PAGE
# -------------------
def home(request):
    trips = TripPlan.objects.all().order_by("-created_at")[:5]
    return render(request, "planner/home.html", {
        "trips": trips
    })

# -------------------
# PLAN PAGE (AI + SAVE TRIP)
# -------------------
def plan(request):
    if request.method == "POST":
        from_city = request.POST.get("from_city")
        destination = request.POST.get("destination")
        budget = request.POST.get("budget")
        style = request.POST.get("style")
        notes = request.POST.get("notes")
        
        # New Fields: Days and Members
        days = int(request.POST.get("days", 3))
        members = int(request.POST.get("members", 1))

        data = {
            "from_city": from_city,
            "destination": destination,
            "budget": budget,
            "style": style,
            "notes": notes,
            "days": days,
            "members": members,
        }

        try:
            # AI GENERATION
            result = planner_agent(data)
            
            # Save AI result in session
            request.session["result"] = result
            request.session.modified = True

            # SAVE PLAN MEMORY (AI HISTORY)
            TripPlan.objects.create(
                from_city=from_city,
                destination=destination,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=days),
                days=days
            )

            # SAVE USER TRIP
            start_date = datetime.today().date()
            end_date = start_date + timedelta(days=days)

            trip = Trip.objects.create(
                from_city=from_city,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                days=days
            )

            request.session["trip_id"] = trip.id

        except Exception as e:
            print("VIEW ERROR:", str(e))
            request.session["result"] = {"error": "AI generation failed"}

        return redirect("result")

    return render(request, "planner/plan.html")

# -------------------
# RESULT PAGE
# -------------------
def result(request):
    result_data = request.session.get("result")
    trip_id = request.session.get("trip_id")

    if not result_data or "error" in result_data:
        return render(request, "planner/result.html", {
            "result": None,
            "error": result_data.get("error", "No plan generated yet") if result_data else "No plan generated yet"
        })

    # 1. TRUST ENGINE
    try:
        result_data["trust"] = evaluate_plan(result_data)
    except Exception as e:
        result_data["trust"] = ["Trust analysis unavailable"]

    # 2. IMAGE ENGINE
    try:
        if "itinerary" in result_data and "route" in result_data:
            for day in result_data["itinerary"]:
                # Use the new 'photo_query' from the AI if available, otherwise fallback
                query = day.get('photo_query') or f"{day.get('title', '')} {result_data['route'].get('to', '')}"
                day["photo"] = get_place_image(query)
    except Exception as e:
        print("IMAGE ENGINE ERROR:", str(e))

    # 3. HOTEL LINK ENGINE
    try:
        if "hotels" in result_data and "route" in result_data:
            destination = result_data["route"].get("to", "")
            for h in result_data["hotels"]:
                h["booking_link"] = hotel_search_link(
                    h.get("name", ""),
                    destination
                )
    except Exception as e:
        print("HOTEL LINK ERROR:", str(e))

    return render(request, "planner/result.html", {
        "result": result_data,
        "trip_id": trip_id,
        "error": None
    })

# -------------------
# ADDITIONAL VIEWS
# -------------------
def add_memory(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        day = request.POST.get("day")
        note = request.POST.get("note")
        photo = request.FILES.get("photo")
        TripMemory.objects.create(trip=trip, day=day, note=note, photo=photo)
        return redirect("trip_dashboard", trip_id=trip.id)
    return render(request, "planner/add_memory.html", {"trip": trip})

def trip_dashboard(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    memories = TripMemory.objects.filter(trip=trip).order_by("day")
    return render(request, "planner/trip_dashboard.html", {"trip": trip, "memories": memories})

def hidden_map(request):
    places = HiddenPlace.objects.all().order_by("-created_at")
    return render(request, "planner/hidden_map.html", {"places": places})

def add_hidden_place(request):
    if request.method == "POST":
        HiddenPlace.objects.create(
            destination=request.POST.get("destination"),
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            latitude=float(request.POST.get("latitude")),
            longitude=float(request.POST.get("longitude")),
            photo=request.FILES.get("photo")
        )
        return redirect("hidden_map")
    return render(request, "planner/add_hidden_place.html")

@require_POST
def delete_hidden_place(request, place_id):
    place = get_object_or_404(HiddenPlace, id=place_id)
    place.delete()
    return redirect("hidden_map")

def demo_result(request):
    # Recruiters can see how the AI handles complex data even in demo mode
    demo = {
        "route": {
            "from": "Chennai",
            "to": "Paris",
            "best_mode": "Flight",
            "options": [
                {"mode": "Emirates First Class", "time": "14 hrs", "cost": "₹1,80,000"}
            ]
        },
        "itinerary": [
            {
                "day": 1, 
                "title": "Private Louvre Tour", 
                "plan": "An after-hours private tour of the Louvre Museum followed by a gourmet dinner overlooking the Seine.", 
                "photo": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800"
            },
            {
                "day": 2, 
                "title": "Eiffel Tower Champagne Experience", 
                "plan": "Exclusive access to the Jules Verne restaurant and a private sunset cruise.", 
                "photo": "https://images.unsplash.com/photo-1543349689-9a4d426bee87?w=800"
            },
        ],
        "hotels": [
            {"name": "The Ritz Paris", "price_per_night": "₹1,10,000", "booking_link": "#"}
        ],
        "budget_summary": {
            "travel": "₹1,80,000",
            "stay": "₹2,20,000",
            "food": "₹45,000",
            "activities": "₹60,000",
            "total": "₹5,05,000"
        },
        "trust": ["Verified Premium Data", "Real-time Route Analysis"]
    }

    return render(request, "planner/result.html", {
        "result": demo,
        "trip_id": None,
        "error": None
    })

@csrf_exempt
def regenerate_day(request):
    if request.method != "POST":
        return redirect("result")
    day_num = request.POST.get("day")
    result_data = request.session.get("result")
    if not result_data or not day_num:
        return redirect("result")
    try:
        idx = int(day_num) - 1
        prompt_data = {
            "from_city": result_data["route"]["from"],
            "destination": result_data["route"]["to"],
            "budget": result_data["budget_summary"]["total"],
            "style": "Adventure",
            "notes": f"Regenerate Day {day_num}"
        }
        new_plan = planner_agent(prompt_data)
        if "itinerary" in new_plan:
            result_data["itinerary"][idx] = new_plan["itinerary"][0]
            request.session["result"] = result_data
            request.session.modified = True
    except: pass
    return redirect("result")
# Add this to your views.py

@require_POST
def delete_trip(request, trip_id):
    trip = get_object_or_404(TripPlan, id=trip_id)
    trip.delete()
    return redirect('home')

def home(request):
    # Fetch all past plans to show in the Expedition Log
    trips = TripPlan.objects.all().order_by("-created_at")
    return render(request, "planner/home.html", {
        "trips": trips
    })