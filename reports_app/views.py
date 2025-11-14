from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts_app.models import Profile


@login_required
def reports_home_view(request):
    """
    صفحة رئيسية للتقارير؛ تظهر فقط للمشرف والمدير.
    """
    profile = Profile.objects.filter(user=request.user).first()
    role = getattr(profile, "role", "employee")

    if role == "employee":
        # ممكن تعرض له رسالة "لا تملك صلاحية"
        return render(request, "reports_app/no_permission.html", {"role": role})

    return render(request, "reports_app/reports_home.html", {"role": role})


@login_required
def building_status_report_view(request):
    """
    تقرير حالة مبنى (مجرود - مضاف - مفقود)
    — Placeholder: لاحقاً نضيف المنطق.
    """
    return render(request, "reports_app/building_status_report.html")


@login_required
def sessions_status_report_view(request):
    """
    تقرير عن حالة جميع الجلسات لموظف أو أكثر.
    — Placeholder: لاحقاً نضيف المنطق.
    """
    return render(request, "reports_app/sessions_status_report.html")


@login_required
def summary_assets_report_view(request):
    """
    تقرير ختامي شامل لكل الأصول المجرودة والمتبقية والمضافة والمفقودة.
    — Placeholder: لاحقاً نضيف المنطق.
    """
    return render(request, "reports_app/summary_assets_report.html")
