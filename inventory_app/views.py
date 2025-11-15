from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.db import models

from locations_app.models import Region, City, Building
from assets_app.models import Asset
from inventory_app.models import InventorySession, InventoryItem

# مكتبات التصدير
import openpyxl
from openpyxl.styles import Font, Alignment


# ============================================================
# الصلاحيات
# ============================================================
def is_employee(user):
    return user.groups.filter(name="employees").exists()


def is_supervisor(user):
    return user.groups.filter(name="supervisors").exists()


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="admins").exists()


# ============================================================
# الموظف — قائمة الجلسات
# ============================================================
@login_required
def sessions_list_view(request):
    sessions = InventorySession.objects.filter(
        employee=request.user
    ).order_by("-start_time")

    return render(request, "inventory_app/sessions_list.html", {
        "sessions": sessions,
    })


# ============================================================
# تفاصيل الجلسة
# ============================================================
@login_required
def session_detail_view(request, session_id):
    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session).select_related("asset")

    # صلاحيات عرض الجلسة:
    if (
        session.employee != request.user
        and not is_supervisor(request.user)
        and not is_admin(request.user)
    ):
        return HttpResponseForbidden("غير مصرح لك")

    return render(request, "inventory_app/session_detail.html", {
        "session": session,
        "items": items,
    })


# ============================================================
# بدء جلسة جرد (موظف أو مدير)
# ============================================================
@login_required
def start_session_view(request):
    if not is_employee(request.user) and not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    regions = Region.objects.all()
    cities = City.objects.all()
    buildings = Building.objects.all()

    if request.method == "POST":
        region = get_object_or_404(Region, id=request.POST.get("region"))
        city = get_object_or_404(City, id=request.POST.get("city"))
        building = get_object_or_404(Building, id=request.POST.get("building"))

        # إنشاء الجلسة
        session = InventorySession.objects.create(
            employee=request.user,
            region=region,
            city=city,
            building=building,
            status="in_progress",
        )

        # إضافة كل الأصول للجلسة
        for asset in Asset.objects.filter(region=region, city=city, building=building):
            InventoryItem.objects.create(
                session=session,
                asset=asset,
                barcode=asset.barcode,
                status="missing",
            )

        return redirect("inventory_app:live_scan", session_id=session.id)

    return render(request, "inventory_app/start_session.html", {
        "regions": regions,
        "cities": cities,
        "buildings": buildings,
    })


# ============================================================
# شاشة المسح
# ============================================================
@login_required
def live_scan_view(request, session_id):
    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user and not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    items = InventoryItem.objects.filter(session=session).select_related("asset")

    return render(request, "inventory_app/session_live_scan.html", {
        "session": session,
        "items": items,
    })


# ============================================================
# API — تسجيل مسح
# ============================================================
@login_required
@require_POST
def scan_update_api(request, session_id):
    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user and not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    barcode = request.POST.get("barcode", "").strip()

    try:
        item = InventoryItem.objects.get(session=session, barcode=barcode)
    except InventoryItem.DoesNotExist:
        return JsonResponse({"status": "not_found"})

    item.status = "found"
    item.scanned_at = timezone.now()
    item.save()

    return JsonResponse({"status": "success"})


# ============================================================
# API — إضافة أصل جديد
# ============================================================
@login_required
@require_POST
def add_new_asset_api(request, session_id):
    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user and not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    barcode = request.POST.get("barcode", "").strip()
    description = request.POST.get("description", "").strip()

    if not barcode or not description:
        return JsonResponse({"status": "error"}, status=400)

    asset = Asset.objects.create(
        barcode=barcode,
        description=description,
        region=session.region,
        city=session.city,
        building=session.building,
    )

    InventoryItem.objects.create(
        session=session,
        asset=asset,
        barcode=barcode,
        status="new",
        added_manually=True,
    )

    return JsonResponse({"status": "success"})


# ============================================================
# إنهاء الجلسة
# ============================================================
@login_required
def close_session(request, session_id):
    session = get_object_or_404(InventorySession, id=session_id)

    if request.method == "POST":
        session.status = "completed"
        session.save()

        return JsonResponse({
            "status": "success",
            "session_id": session.id
        })

    return JsonResponse({"status": "invalid"}, status=400)


# ============================================================
# إرسال للمشرف
# ============================================================
@login_required
@require_POST
def submit_to_supervisor(request, session_id):
    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user and not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    session.status = "submitted_to_supervisor"
    session.save()

    return JsonResponse({"status": "success"})


# ============================================================
# المشرف — قائمة الجلسات
# ============================================================
@login_required
def supervisor_sessions_list(request):
    if not is_supervisor(request.user) and not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    sessions = InventorySession.objects.filter(status="submitted_to_supervisor")

    return render(request, "inventory_app/supervisor_sessions_list.html", {
        "sessions": sessions,
    })


# ============================================================
# المشرف — تفاصيل الجلسة
# ============================================================
@login_required
def supervisor_session_detail(request, session_id):
    if not is_supervisor(request.user) and not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session)

    return render(request, "inventory_app/supervisor_session_detail.html", {
        "session": session,
        "items": items,
    })


# ============================================================
# المشرف — موافقة
# ============================================================
@login_required
@require_POST
def supervisor_approve_session(request, session_id):
    if not is_supervisor(request.user) and not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    session = get_object_or_404(InventorySession, id=session_id)

    session.status = "supervisor_approved"
    session.supervisor = request.user
    session.save()

    return JsonResponse({"status": "success"})


# ============================================================
# المشرف — رفض
# ============================================================
@login_required
@require_POST
def supervisor_reject_session(request, session_id):
    if not is_supervisor(request.user) and not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    session = get_object_or_404(InventorySession, id=session_id)
    comment = request.POST.get("comment", "").strip()

    session.status = "supervisor_rejected"
    session.supervisor = request.user
    session.supervisor_comment = comment
    session.save()

    return JsonResponse({"status": "success"})


# ============================================================
# المدير — قائمة الجلسات
# ============================================================
@login_required
def admin_sessions_list(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    sessions = InventorySession.objects.all().order_by("-start_time")

    return render(request, "inventory_app/admin_sessions_list.html", {
        "sessions": sessions,
    })


# ============================================================
# المدير — تفاصيل الجلسة
# ============================================================
@login_required
def admin_session_detail(request, session_id):

    if not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session)

    return render(request, "inventory_app/admin_session_detail.html", {
        "session": session,
        "items": items,
    })


# ============================================================
# المدير — إعادة فتح الجلسة
# ============================================================
@login_required
@require_POST
def admin_reopen_session(request, session_id):

    if not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    session = get_object_or_404(InventorySession, id=session_id)

    session.status = "in_progress"
    session.end_time = None
    session.supervisor = None
    session.supervisor_comment = ""
    session.save()

    return JsonResponse({"status": "success"})


# ============================================================
# المدير — حذف الجلسة
# ============================================================
@login_required
@require_POST
def admin_delete_session(request, session_id):

    if not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    try:
        session = InventorySession.objects.get(id=session_id)
        session.delete()
        return JsonResponse({"status": "success"})

    except InventorySession.DoesNotExist:
        return JsonResponse({"status": "error", "message": "الجلسة غير موجودة"})


# ============================================================
# تصدير PDF
# ============================================================
@login_required
def export_session_pdf(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session).select_related("asset")

    html = render_to_string("inventory_app/report_template.html", {
        "session": session,
        "items": items,
    })

    from xhtml2pdf import pisa
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="session_{session_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("خطأ أثناء إنشاء ملف PDF", status=500)

    return response


# ============================================================
# تصدير Excel
# ============================================================
@login_required
def export_session_excel(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session).select_related("asset")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventory Session"

    headers = ["الباركود", "الوصف", "الحالة", "وقت المسح"]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for item in items:
        ws.append([
            item.barcode,
            item.asset.description,
            item.status,
            item.scanned_at.strftime("%Y-%m-%d %H:%M") if item.scanned_at else "-",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="session_{session_id}.xlsx"'

    wb.save(response)
    return response

# ===========================
# مدير النظام — لوحة التحكم Dashboard
# ===========================
@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك (Admin فقط)")

    # إحصائيات عامة
    total_sessions = InventorySession.objects.count()
    completed = InventorySession.objects.filter(status="completed").count()
    submitted = InventorySession.objects.filter(status="submitted_to_supervisor").count()
    approved = InventorySession.objects.filter(status="supervisor_approved").count()
    rejected = InventorySession.objects.filter(status="supervisor_rejected").count()

    # أحدث الجلسات (آخر 5)
    latest_sessions = InventorySession.objects.select_related(
        "employee", "region", "building"
    ).order_by("-start_time")[:5]

    # أفضل الموظفين نشاطاً
    top_users = InventorySession.objects.values("employee__username") \
        .annotate(count=models.Count("id")) \
        .order_by("-count")[:5]

    return render(request, "inventory_app/admin_dashboard.html", {
        "total_sessions": total_sessions,
        "completed": completed,
        "submitted": submitted,
        "approved": approved,
        "rejected": rejected,
        "latest_sessions": latest_sessions,
        "top_users": top_users,
    })

# ===========================
# مدير النظام — حذف الجلسة
# ===========================
@login_required
@require_POST
def admin_delete_session(request, session_id):

    if not is_admin(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    try:
        session = InventorySession.objects.get(id=session_id)
        session.delete()
        return JsonResponse({"status": "success"})

    except InventorySession.DoesNotExist:
        return JsonResponse({"status": "error", "message": "الجلسة غير موجودة"})
