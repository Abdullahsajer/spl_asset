from django.urls import path
from . import views

app_name = "inventory_app"

urlpatterns = [

    # قائمة الجلسات
    path('sessions/', views.sessions_list_view, name='sessions_list'),

    # تفاصيل جلسة معينة
    path('sessions/<int:session_id>/', views.session_detail_view, name='session_detail'),

    # بدء جلسة جرد جديدة
    path('sessions/start/', views.start_session_view, name='start_session'),

    # شاشة المسح المستمر
    path('sessions/<int:session_id>/scan/', views.live_scan_view, name='live_scan'),
]
