from django.urls import path
from . import views

app_name = "assets_app"

urlpatterns = [
    path("list/", views.assets_list_view, name="assets_list"),
    path("<int:asset_id>/", views.asset_detail_view, name="asset_detail"),
]
