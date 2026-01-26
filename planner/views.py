from django.shortcuts import render, redirect, get_object_or_404
from .ai_agent import planner_agent
from .free_images import get_place_image
from .trust_engine import evaluate_plan
from .models import Trip, TripMemory, HiddenPlace
from datetime import datetime, timedelta

# -------------------
# HOME PAGE
# -------------------
def home(request):
    return render(request, "planner/home.html")


# -------------------
# PLAN PAGE (AI + SAVE TRIP)
# -------------------
def plan(request):
    print("PLAN VIEW HIT")

    if request.method == "POST":
        print("POST RECEIVED")

        from_city = request.POST.get("from_city")
        destination = request.POST.get("destination")
        budget = request.POST.get("budget")
        style = request.POST.get("style")
        notes = request.POST.get("notes")

        print("FORM DATA:", from_city, destination, budget, style, notes)

        data = {
            "from_city": from_city,
            "destination": destination,
            "budget": budget,
            "style": style,
            "notes": notes,
        }

        try:
            # -------------------
            # AI GENERATION
            # -------------------
            result = planner_agent(data)
            print("AI RESULT:", result)

            # Save result in session
            request.session["result"] = result
            request.session.modified = True

            # -------------------
            # SAVE TRIP TO DB
            # -------------------
            start_date = datetime.today().date()
            days = 3
            end_date = start_date + timedelta(days=days)

            trip = Trip.objects.create(
                from_city=from_city,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                days=days
            )

            request.session["trip_id"] = trip.id
            print("TRIP SAVED:", trip.id)

        except Exception as e:
            print("VIEW ERROR:", str(e))
            request.session["result"] = {"error": "AI generation failed"}

        return redirect("result")

    return render(request, "planner/plan.html")


# -------------------
# RESULT PAGE
# -------------------
def result(request):
    print("RESULT VIEW HIT")

    result_data = request.session.get("result")
    trip_id = request.session.get("trip_id")

    print("SESSION DATA:", result_data)

    if not result_data or "error" in result_data:
        return render(request, "planner/result.html", {
            "result": None,
            "error": result_data.get("error", "No plan generated yet")
        })

    # -------------------
    # TRUST ENGINE
    # -------------------
    try:
        result_data["trust"] = evaluate_plan(result_data)
    except Exception as e:
        print("TRUST ENGINE ERROR:", str(e))
        result_data["trust"] = ["Trust analysis unavailable"]

    # -------------------
    # IMAGE ENGINE
    # -------------------
    try:
        if "itinerary" in result_data and "route" in result_data:
            for day in result_data["itinerary"]:
                place = f"{day.get('title', '')} {result_data['route'].get('to', '')}"
                day["photo"] = get_place_image(place)
    except Exception as e:
        print("IMAGE ENGINE ERROR:", str(e))

    return render(request, "planner/result.html", {
        "result": result_data,
        "trip_id": trip_id,
        "error": None
    })


# -------------------
# ADD MEMORY PAGE
# -------------------
def add_memory(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == "POST":
        day = request.POST.get("day")
        note = request.POST.get("note")
        photo = request.FILES.get("photo")

        TripMemory.objects.create(
            trip=trip,
            day=day,
            note=note,
            photo=photo
        )

        return redirect("trip_dashboard", trip_id=trip.id)

    return render(request, "planner/add_memory.html", {
        "trip": trip
    })


# -------------------
# TRIP DASHBOARD
# -------------------
def trip_dashboard(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    memories = TripMemory.objects.filter(trip=trip).order_by("day")

    return render(request, "planner/trip_dashboard.html", {
        "trip": trip,
        "memories": memories
    })


# -------------------
# HIDDEN GEMS MAP
# -------------------
def hidden_map(request):
    places = HiddenPlace.objects.all().order_by("-created_at")

    return render(request, "planner/hidden_map.html", {
        "places": places
    })


# -------------------
# ADD HIDDEN PLACE
# -------------------
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
from .models import HiddenPlace
from django.views.decorators.http import require_POST

@require_POST
def delete_hidden_place(request, place_id):
    place = get_object_or_404(HiddenPlace, id=place_id)
    place.delete()
    return redirect("hidden_map")
