from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST

from locations_app.models import Region, City, Building
from assets_app.models import Asset
from .models import InventorySession, InventoryItem


# ===========================
# الصلاحيات
# ===========================
def is_employee(user):
    return user.groups.filter(name="employees").exists()

def is_supervisor(user):
    return user.groups.filter(name="supervisors").exists()

def is_admin(user):
    return user.is_superuser or user.groups.filter(name="admins").exists()


# ===========================
# جلسات الموظف
# ===========================
@login_required
def sessions_list_view(request):
    """يرى الموظف جلساته فقط"""
    sessions = InventorySession.objects.filter(
        employee=request.user
    ).order_by("-start_time")

    return render(request, "inventory_app/sessions_list.html", {
        "sessions": sessions,
    })


# ===========================
# تفاصيل الجلسة (لموظف + مشرف)
# ===========================
@login_required
def session_detail_view(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session).select_related("asset")

    # منع غير الموظف والمشرف
    if session.employee != request.user and not is_supervisor(request.user):
        return HttpResponseForbidden("غير مصرح لك بالدخول")

    return render(request, "inventory_app/session_detail.html", {
        "session": session,
        "items": items,
    })


# ===========================
# بدء جلسة جرد — الموظف فقط
# ===========================
@login_required
def start_session_view(request):

    if not is_employee(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    regions = Region.objects.all()
    cities = City.objects.all()
    buildings = Building.objects.all()

    if request.method == "POST":
        region = get_object_or_404(Region, id=request.POST.get("region"))
        city = get_object_or_404(City, id=request.POST.get("city"))
        building = get_object_or_404(Building, id=request.POST.get("building"))

        session = InventorySession.objects.create(
            employee=request.user,
            region=region, city=city, building=building,
            status="in_progress"
        )

        # تحميل الأصول
        assets = Asset.objects.filter(region=region, city=city, building=building)

        for asset in assets:
            InventoryItem.objects.create(
                session=session,
                asset=asset,
                barcode=asset.barcode,
                status="missing"
            )

        return redirect("inventory_app:live_scan", session_id=session.id)

    return render(request, "inventory_app/start_session.html", {
        "regions": regions,
        "cities": cities,
        "buildings": buildings,
    })


# ===========================
# شاشة المسح — الموظف فقط
# ===========================
@login_required
def live_scan_view(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user:
        return HttpResponseForbidden("غير مصرح لك")

    items = InventoryItem.objects.filter(session=session).select_related("asset")

    return render(request, "inventory_app/session_live_scan.html", {
        "session": session,
        "items": items,
    })


# ===========================
# API: تسجيل مسح
# ===========================
@login_required
@require_POST
def scan_update_api(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user:
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

# ===========================
# API — إضافة أصل جديد أثناء الجرد
# ===========================
@login_required
@require_POST
def add_new_asset_api(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)

    # فقط الموظف له حق الإضافة
    if session.employee != request.user:
        return JsonResponse({"status": "forbidden"}, status=403)

    barcode = request.POST.get("barcode", "").strip()
    description = request.POST.get("description", "").strip()

    if not barcode or not description:
        return JsonResponse({
            "status": "error",
            "message": "يجب إدخال الباركود والوصف."
        }, status=400)

    # إنشاء الأصل الجديد
    asset = Asset.objects.create(
        barcode=barcode,
        description=description,
        region=session.region,
        city=session.city,
        building=session.building,
    )

    # إضافة الأصل للجلسة الحالية مباشرة
    InventoryItem.objects.create(
        session=session,
        asset=asset,
        barcode=barcode,
        status="new",
        added_manually=True
    )

    return JsonResponse({
        "status": "success",
        "message": "تمت إضافة الأصل الجديد بنجاح.",
        "barcode": barcode
    })




# ===========================
# الموظف ينهي الجلسة
# ===========================
@login_required
@require_POST
def close_session(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user:
        return JsonResponse({"status": "forbidden"}, status=403)

    session.status = "completed"
    session.end_time = timezone.now()
    session.save()

    return JsonResponse({"status": "success"})


# ===========================
# الموظف يرسل للمشرف
# ===========================
@login_required
@require_POST
def submit_to_supervisor(request, session_id):

    session = get_object_or_404(InventorySession, id=session_id)

    if session.employee != request.user:
        return JsonResponse({"status": "forbidden"}, status=403)

    session.status = "submitted_to_supervisor"
    session.save()

    return JsonResponse({"status": "success"})


# ===========================
# المشرف يشاهد كل الجلسات
# ===========================
@login_required
def supervisor_sessions_list(request):

    if not is_supervisor(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    sessions = InventorySession.objects.filter(
        status="submitted_to_supervisor"
    ).order_by("-start_time")

    return render(request, "inventory_app/supervisor_sessions_list.html", {
        "sessions": sessions
    })


# ===========================
# تفاصيل جلسة لدى المشرف
# ===========================
@login_required
def supervisor_session_detail(request, session_id):

    if not is_supervisor(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session).select_related("asset")

    return render(request, "inventory_app/supervisor_session_detail.html", {
        "session": session,
        "items": items,
    })


# ===========================
# موافقة المشرف
# ===========================
@login_required
@require_POST
def supervisor_approve_session(request, session_id):

    if not is_supervisor(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    session = get_object_or_404(InventorySession, id=session_id)
    session.status = "supervisor_approved"
    session.supervisor = request.user
    session.save()

    return JsonResponse({"status": "success"})


# ===========================
# رفض المشرف
# ===========================
@login_required
@require_POST
def supervisor_reject_session(request, session_id):

    if not is_supervisor(request.user):
        return JsonResponse({"status": "forbidden"}, status=403)

    session = get_object_or_404(InventorySession, id=session_id)
    comment = request.POST.get("comment", "")

    session.status = "supervisor_rejected"
    session.supervisor = request.user
    session.supervisor_comment = comment
    session.save()

    return JsonResponse({"status": "success"})
