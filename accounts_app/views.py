from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout

from .models import Profile


# ============================
#   لوحة التحكم Dashboard
# ============================
@login_required
def dashboard_view(request):
    """
    يعرض لوحة تحكم تختلف حسب دور المستخدم:
    - موظف: يظهر له رابط جلسات الجرد
    - مشرف: يظهر له جلسات المراجعة
    - مدير: يظهر له لوحة تقارير النظام
    """
    profile = Profile.objects.filter(user=request.user).first()
    role = getattr(profile, "role", "employee")

    context = {
        "role": role,
        "user": request.user,
    }

    return render(request, "accounts_app/dashboard.html", context)


# ============================
#   صفحة البيانات الشخصية
# ============================
@login_required
def profile_view(request):
    """
    يعرض صفحة معلومات المستخدم والدور الخاص به.
    """
    profile = Profile.objects.filter(user=request.user).first()

    return render(request, "accounts_app/profile.html", {
        "user": request.user,
        "profile": profile,
    })


# ============================
#   تسجيل الدخول
# ============================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("accounts_app:dashboard")
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة")

    return render(request, "accounts_app/login.html")


# ============================
#   تسجيل الخروج
# ============================
@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts_app:login")


# ============================
#   إنشاء حساب جديد (اختياري)
# ============================
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # تحقق من تطابق كلمة المرور
        if password1 != password2:
            messages.error(request, "كلمتا المرور غير متطابقتين")
            return redirect("accounts_app:register")

        # تحقق من عدم وجود المستخدم مسبقًا
        if User.objects.filter(username=username).exists():
            messages.error(request, "اسم المستخدم مستخدم مسبقًا")
            return redirect("accounts_app:register")

        # إنشاء مستخدم جديد
        user = User.objects.create_user(username=username, password=password1)
        Profile.objects.create(user=user, role="employee")  # قيمة افتراضية

        messages.success(request, "تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
        return redirect("accounts_app:login")

    return render(request, "accounts_app/register.html")
