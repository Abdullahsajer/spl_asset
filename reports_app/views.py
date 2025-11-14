from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def reports_home_view(request):
    return render(request, "reports_app/reports_home.html")


@login_required
def building_status_report_view(request):
    return render(request, "reports_app/building_status_report.html")


@login_required
def sessions_status_report_view(request):
    return render(request, "reports_app/sessions_status_report.html")


@login_required
def summary_assets_report_view(request):
    return render(request, "reports_app/summary_assets_report.html")
