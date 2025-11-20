from django.urls import path
from . import views

app_name = "inventory_app"

urlpatterns = [

    # ========================
    #  موظف Employee
    # ========================

    # قائمة الجلسات
    path("sessions/", views.sessions_list_view, name="sessions_list"),

    # تفاصيل جلسة
    path("sessions/<int:session_id>/", views.session_detail_view, name="session_detail"),

    # بدء جلسة جديدة
    path("sessions/start/", views.start_session_view, name="start_session"),

    # شاشة المسح
    path("sessions/<int:session_id>/scan/", views.live_scan_view, name="live_scan"),

    # API تحديث حالة المسح
    path("sessions/<int:session_id>/scan/update/", views.scan_update_api, name="scan_update_api"),

    # حفظ الجلسة مؤقتاً
    path("sessions/<int:session_id>/draft/", views.save_draft_session, name="save_draft_session"),

    # إنهاء الجلسة
    path("sessions/<int:session_id>/close/", views.close_session, name="close_session"),

    # إضافة أصل جديد
    path("sessions/<int:session_id>/add_new_asset/", views.add_new_asset_api, name="add_new_asset_api"),

    # ترحيل للمشرف
    path("sessions/<int:session_id>/submit/", views.submit_to_supervisor, name="submit_to_supervisor"),
    # تأكيد يدوي
    path("sessions/<int:session_id>/manual-confirm/", views.manual_confirm_api, name="manual_confirm_api"),



    # ========================
    # API — المدن والمباني
    # ========================
    path("api/get-cities/<int:region_id>/", views.get_cities_by_region, name="get_cities_by_region"),
    path("api/get-buildings/<int:city_id>/", views.get_buildings_by_city, name="get_buildings_by_city"),


    # API بيانات أصل لصفحة النسخ
    path("api/assets/get/<str:barcode>/", views.get_asset_api, name="get_asset_api"),


    # ========================
    # المشرف Supervisor
    # ========================

    path("supervisor/sessions/", views.supervisor_sessions_list, name="supervisor_sessions_list"),
    path("supervisor/sessions/<int:session_id>/", views.supervisor_session_detail, name="supervisor_session_detail"),
    path("supervisor/sessions/<int:session_id>/approve/", views.supervisor_approve_session, name="supervisor_approve_session"),
    path("supervisor/sessions/<int:session_id>/reject/", views.supervisor_reject_session, name="supervisor_reject_session"),


    # ========================
    # المدير Admin
    # ========================
    path("admin-panel/sessions/", views.admin_sessions_list, name="admin_sessions_list"),
    path("admin-panel/sessions/<int:session_id>/", views.admin_session_detail, name="admin_session_detail"),
    path("admin-panel/sessions/<int:session_id>/reopen/", views.admin_reopen_session, name="admin_reopen_session"),
    path("admin-panel/sessions/delete/<int:session_id>/", views.admin_delete_session, name="admin_delete_session"),

    # استيراد الأصول
    path("admin/import-assets/", views.admin_import_assets, name="admin_import_assets"),

    # النسخة الاحتياطية
    path("admin/backup-full/", views.backup_full_system, name="backup_full_system"),

    # لوحة التحكم
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # تصدير PDF / Excel
    path("sessions/<int:session_id>/export/pdf/", views.export_session_pdf, name="export_session_pdf"),
    path("sessions/<int:session_id>/export/excel/", views.export_session_excel, name="export_session_excel"),

]
