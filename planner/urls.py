from django.urls import path
from . import views

urlpatterns = [
    # Core Pages
    path("", views.home, name="home"),
    path("plan/", views.plan, name="plan"),
    path("result/", views.result, name="result"),

    # Trips & Memories
    path("trip/<int:trip_id>/", views.trip_dashboard, name="trip_dashboard"),
    path("trip/<int:trip_id>/add/", views.add_memory, name="add_memory"),

    # Hidden Gems System
    path("result/map/", views.hidden_map, name="hidden_map"),

    path("add-place/", views.add_hidden_place, name="add_hidden_place"),
    path("map/", views.hidden_map, name="hidden_map"),

    path("delete-place/<int:place_id>/", views.delete_hidden_place, name="delete_hidden_place"),

]
