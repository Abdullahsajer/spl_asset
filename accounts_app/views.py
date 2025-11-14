from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile


@login_required
def dashboard_view(request):
    """
    لوحة بسيطة لعرض دور المستخدم وبعض المعلومات.
    """
    profile = Profile.objects.filter(user=request.user).first()
    role = profile.get_role_display() if profile else "موظف"

    context = {
        "user": request.user,
        "profile": profile,
        "role": role,
    }
    return render(request, "accounts_app/dashboard.html", context)


@login_required
def profile_view(request):
    """
    صفحة عرض بيانات المستخدم الشخصية.
    """
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, "accounts_app/profile.html", {
        "user": request.user,
        "profile": profile,
    })
