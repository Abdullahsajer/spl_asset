from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Region, City, Building


@login_required
def regions_list_view(request):
    regions = Region.objects.all().order_by("name")
    return render(request, "locations_app/regions_list.html", {"regions": regions})


@login_required
def cities_list_view(request):
    cities = City.objects.select_related("region").all().order_by("region__name", "name")
    return render(request, "locations_app/cities_list.html", {"cities": cities})


@login_required
def buildings_list_view(request):
    buildings = Building.objects.select_related("city", "city__region").all().order_by(
        "city__region__name", "city__name", "name"
    )
    return render(request, "locations_app/buildings_list.html", {"buildings": buildings})
