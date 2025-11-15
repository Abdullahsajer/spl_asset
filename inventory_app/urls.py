from django.urls import path
from . import views

app_name = "inventory_app"

urlpatterns = [

    # ========================
    #  موظف Employee
    # ========================

    # قائمة الجلسات الخاصة بالموظف
    path("sessions/", views.sessions_list_view, name="sessions_list"),

    # تفاصيل جلسة
    path("sessions/<int:session_id>/", views.session_detail_view, name="session_detail"),

    # بدء جلسة جديدة
    path("sessions/start/", views.start_session_view, name="start_session"),

    # شاشة المسح
    path("sessions/<int:session_id>/scan/", views.live_scan_view, name="live_scan"),

    # تحديث حالة المسح (API)
    path("sessions/<int:session_id>/scan/update/", views.scan_update_api, name="scan_update_api"),

    # إغلاق الجلسة (الدالة الصحيحة)
    path("sessions/<int:session_id>/close/", views.close_session, name="close_session"),

    # إضافة أصل جديد أثناء الجرد (API)
    path("sessions/<int:session_id>/add_new_asset/", views.add_new_asset_api, name="add_new_asset_api"),

    # تقديم الجلسة للمشرف
    path("sessions/<int:session_id>/submit/", views.submit_to_supervisor, name="submit_to_supervisor"),


    # ========================
    #  مشرف Supervisor
    # ========================

    # قائمة الجلسات التي تنتظر المراجعة
    path("supervisor/sessions/", views.supervisor_sessions_list, name="supervisor_sessions_list"),

    # تفاصيل جلسة للمشرف
    path("supervisor/sessions/<int:session_id>/", views.supervisor_session_detail, name="supervisor_session_detail"),

    # موافقة المشرف
    path("supervisor/sessions/<int:session_id>/approve/", views.supervisor_approve_session, name="supervisor_approve_session"),

    # رفض المشرف
    path("supervisor/sessions/<int:session_id>/reject/", views.supervisor_reject_session, name="supervisor_reject_session"),

    # ========================
    #  صفحات المدير Admin
    # ========================
    path("admin-panel/sessions/", views.admin_sessions_list, name="admin_sessions_list"),
    path("admin-panel/sessions/<int:session_id>/", views.admin_session_detail, name="admin_session_detail"),
    path("admin-panel/sessions/<int:session_id>/reopen/", views.admin_reopen_session, name="admin_reopen_session"),
    path("admin-panel/sessions/delete/<int:session_id>/", views.admin_delete_session, name="admin_delete_session"),


    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # === تقارير PDF/Excel ===
    path("sessions/<int:session_id>/export/pdf/", views.export_session_pdf, name="export_session_pdf"),
    path("sessions/<int:session_id>/export/excel/", views.export_session_excel, name="export_session_excel"),


]
