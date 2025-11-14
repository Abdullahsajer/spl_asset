from django.urls import path
from . import views

app_name = "reports_app"

urlpatterns = [
    path('', views.reports_home_view, name='reports_home'),

    path('building-status/', views.building_status_report_view, name='building_status_report'),
    path('sessions-status/', views.sessions_status_report_view, name='sessions_status_report'),
    path('summary/', views.summary_assets_report_view, name='summary_assets_report'),
]
