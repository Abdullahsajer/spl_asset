from django.urls import path
from . import views

app_name = "locations_app"

urlpatterns = [

    # ================================
    # 📍 صفحات عرض البيانات
    # ================================
    path("regions/", views.regions_list_view, name="regions_list"),
    path("cities/", views.cities_list_view, name="cities_list"),
    path("buildings/", views.buildings_list_view, name="buildings_list"),

    # ================================
    # 📥 صفحات الاستيراد (Excel)
    # ================================
    path("import-regions/", views.admin_import_regions, name="admin_import_regions"),
    path("import-cities/", views.admin_import_cities, name="admin_import_cities"),
    path("import-buildings/", views.admin_import_buildings, name="admin_import_buildings"),
]
