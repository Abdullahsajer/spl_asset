from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts_app"

urlpatterns = [

    # الصفحات الداخلية
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),

    # تسجيل الدخول + تسجيل الخروج
    path("login/", auth_views.LoginView.as_view(template_name="accounts_app/login.html"), name="login"),
    

    # إنشاء حساب (اختياري)
    path("register/", views.register_view, name="register"),
]
