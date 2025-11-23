from django.shortcuts import render
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import Group

def home(request):
    groups = []
    if request.user.is_authenticated:
        groups = list(request.user.groups.values_list("name", flat=True))

    return render(request, "home.html", {
        "groups": groups,
    })


urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('accounts_app.urls')),
    path('locations/', include('locations_app.urls')),
    path('assets/', include('assets_app.urls')),
    path('inventory/', include('inventory_app.urls')),
    path('reports/', include('reports_app.urls')),
    path('admin/', admin.site.urls),
    path("import/", include("import_app.urls")),
    

]
