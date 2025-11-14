from django.urls import path
from . import views

app_name = "locations_app"

urlpatterns = [
    path("regions/", views.regions_list_view, name="regions_list"),
    path("cities/", views.cities_list_view, name="cities_list"),
    path("buildings/", views.buildings_list_view, name="buildings_list"),
]
