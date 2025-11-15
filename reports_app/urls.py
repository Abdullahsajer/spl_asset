from django.urls import path
from . import views

app_name = "reports_app"

urlpatterns = [

    # صفحات التقارير
    path("", views.reports_home_view, name="reports_home"),
    path("building-status/", views.building_status_report_view, name="building_status_report"),
    path("sessions-status/", views.sessions_status_report_view, name="sessions_status_report"),
    path("summary/", views.summary_assets_report_view, name="summary_assets_report"),

    # AJAX APIs
    path("ajax/get-cities/<int:region_id>/", views.get_cities_ajax, name="get_cities_ajax"),
    path("ajax/get-buildings/<int:city_id>/", views.get_buildings_ajax, name="get_buildings_ajax"),
]
