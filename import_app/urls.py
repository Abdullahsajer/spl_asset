from django.urls import path
from . import views

app_name = "import_app"

urlpatterns = [
    path("", views.import_step1_upload, name="step1"),
    path("step2/", views.import_step2_choose_table, name="step2"),
    path("step3/", views.import_step3_mapping, name="step3"),
    path("apply/", views.import_step4_apply, name="apply"),
    path("logs/", views.import_logs, name="logs"),

]
