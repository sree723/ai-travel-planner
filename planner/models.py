from django.db import models


# -------------------
# MAIN TRIP RECORD
# -------------------
class Trip(models.Model):
    from_city = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_city} → {self.destination}"


# -------------------
# USER TRIP MEMORIES
# -------------------
class TripMemory(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="memories")
    day = models.IntegerField()
    note = models.TextField(blank=True)
    photo = models.ImageField(upload_to="trip_memories/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Memory Day {self.day} — {self.trip.destination}"


# -------------------
# HIDDEN GEMS SYSTEM
# -------------------
class HiddenPlace(models.Model):
    destination = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    photo = models.ImageField(upload_to="hidden_places/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.destination}"


# -------------------
# OPTIONAL: PLANNING SNAPSHOT
# -------------------
class TripPlan(models.Model):
    from_city = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_city} → {self.destination} ({self.days} days)"
