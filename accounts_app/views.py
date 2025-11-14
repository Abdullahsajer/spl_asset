from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile


@login_required
def dashboard_view(request):
    """
    لوحة بسيطة تختلف حسب دور المستخدم:
    - موظف جرد: توجيه لشاشة جلسات الجرد
    - مشرف / مدير نظام: توجيه لشاشة الجلسات/التقارير
    """
    profile = Profile.objects.filter(user=request.user).first()
    role = getattr(profile, "role", "employee")

    context = {
        "role": role,
    }
    return render(request, "accounts_app/dashboard.html", context)


@login_required
def profile_view(request):
    """
    صفحة عرض بيانات المستخدم ودوره.
    """
    profile = Profile.objects.filter(user=request.user).first()
    context = {
        "user": request.user,
        "profile": profile,
    }
    return render(request, "accounts_app/profile.html", context)
