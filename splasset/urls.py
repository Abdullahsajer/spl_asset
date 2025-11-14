from django.shortcuts import render
from django.contrib import admin
from django.urls import path, include

def home(request):
    return render(request, "home.html")

urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('accounts_app.urls')),
    path('locations/', include('locations_app.urls')),
    path('assets/', include('assets_app.urls')),
    path('inventory/', include('inventory_app.urls')),
    path('reports/', include('reports_app.urls')),
    path('admin/', admin.site.urls),
]
