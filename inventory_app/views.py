from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.db import models
import openpyxl
from django.contrib import messages
from django.shortcuts import render
from django.db import transaction

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
# 🔵 API — جلب المدن حسب المنطقة
# ============================================================
@login_required
def get_cities_by_region(request, region_id):
    cities = City.objects.filter(region_id=region_id).values("id", "name")
    return JsonResponse(list(cities), safe=False)


# ============================================================
# 🔵 API — جلب المباني حسب المدينة
# ============================================================
@login_required
def get_buildings_by_city(request, city_id):
    buildings = Building.objects.filter(city_id=city_id).values("id", "name")
    return JsonResponse(list(buildings), safe=False)


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


# ============================================================
# استيراد الأصول
# ============================================================
@login_required
def admin_import_assets(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("غير مسموح لك")

    if request.method == "POST" and request.FILES.get("excel_file"):

        file = request.FILES["excel_file"]

        try:
            wb = openpyxl.load_workbook(file, data_only=True)
            ws = wb.active
        except:
            messages.error(request, "❌ خطأ: الملف غير صالح، تأكد أنه Excel بصيغة .xlsx")
            return redirect("inventory_app:admin_import_assets")

        # قراءة أسماء الأعمدة من الصف الأول
        headers = [str(c.value).strip() if c.value else "" for c in ws[1]]

        # تحويلها لتعامل باسم العمود
        col = {name: index for index, name in enumerate(headers)}

        # التحقق أن كل الأعمدة المطلوبة موجودة
        required_cols = [
            "asset_code", "barcode", "old_barcode", "description",
            "main_category", "type", "sub_category",
            "region_name", "city_name", "building_name",
            "status", "condition",
            "custodian_number", "custodian_name", "custodian_type",
            "created_at", "created_by_username",
        ]

        missing = [c for c in required_cols if c not in col]
        if missing:
            messages.error(request, f"❌ الأعمدة المفقودة: {', '.join(missing)}")
            return redirect("inventory_app:admin_import_assets")

        added = 0
        skipped = 0
        errors = []

        with transaction.atomic():
            for row_number, row in enumerate(ws.iter_rows(min_row=2), start=2):

                try:
                    # استخراج البيانات باستخدام اسم كل عمود (وليس ترتيب الأعمدة)
                    get = lambda field: row[col[field]].value if col[field] < len(row) else None

                    asset_code       = get("asset_code")
                    barcode          = get("barcode")
                    old_barcode      = get("old_barcode")
                    description      = get("description")
                    main_category    = get("main_category")
                    type_            = get("type")
                    sub_category     = get("sub_category")
                    region_name      = get("region_name")
                    city_name        = get("city_name")
                    building_name    = get("building_name")
                    status           = get("status")
                    condition        = get("condition")
                    custodian_number = get("custodian_number")
                    custodian_name   = get("custodian_name")
                    custodian_type   = get("custodian_type")
                    created_at       = get("created_at")
                    created_by_username = get("created_by_username")

                    # تجاهل الصف إذا asset_code أو barcode غير موجود
                    if not asset_code or not barcode:
                        skipped += 1
                        errors.append(f"سطر {row_number}: asset_code أو barcode فارغ")
                        continue

                    # جلب الموقع
                    region = Region.objects.filter(name=str(region_name).strip()).first()
                    city = City.objects.filter(name=str(city_name).strip()).first()
                    building = Building.objects.filter(name=str(building_name).strip()).first()

                    if not region or not city or not building:
                        skipped += 1
                        errors.append(f"سطر {row_number}: بيانات الموقع غير صحيحة")
                        continue

                    # إنشاء الأصل
                    Asset.objects.create(
                        asset_code=asset_code,
                        barcode=barcode,
                        old_barcode=old_barcode,
                        description=description,
                        main_category=main_category,
                        type=type_,
                        sub_category=sub_category,
                        region=region,
                        city=city,
                        building=building,
                        status=status,
                        condition=condition,
                        custodian_number=custodian_number,
                        custodian_name=custodian_name,
                        custodian_type=custodian_type,
                        created_at=created_at,
                        created_by_username=created_by_username,
                    )

                    added += 1

                except Exception as e:
                    skipped += 1
                    errors.append(f"سطر {row_number}: {str(e)}")

        return render(request, "inventory_app/admin_import_result.html", {
            "added": added,
            "skipped": skipped,
            "errors": errors,
        })

    return render(request, "inventory_app/admin_import_assets.html")


# ============================================================
# النسخة الاحتياطية الكاملة
# ============================================================
@login_required
def backup_full_system(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("غير مصرح لك")

    wb = openpyxl.Workbook()

    # ============================================================
    # Sheet 1 — ملخص الجلسات
    # ============================================================
    ws1 = wb.active
    ws1.title = "Sessions_Summary"

    headers1 = [
        "session_id", "employee",
        "region", "city", "building",
        "status", "start_time", "end_time",
        "total_items", "found_items",
        "missing_items", "new_items",
    ]
    ws1.append(headers1)

    sessions = InventorySession.objects.select_related(
        "employee", "region", "city", "building"
    )

    for session in sessions:
        items = InventoryItem.objects.filter(session=session)

        ws1.append([
            session.id,
            session.employee.username if session.employee else "",
            session.region.name if session.region else "",
            session.city.name if session.city else "",
            session.building.name if session.building else "",
            session.status,
            session.start_time.strftime("%Y-%m-%d %H:%M") if session.start_time else "",
            session.end_time.strftime("%Y-%m-%d %H:%M") if session.end_time else "",
            items.count(),
            items.filter(status="found").count(),
            items.filter(status="missing").count(),
            items.filter(status="new").count(),
        ])

    for cell in ws1[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # ============================================================
    # Sheet 2 — تفاصيل العناصر
    # ============================================================
    ws2 = wb.create_sheet(title="Items_Details")

    headers2 = [
        "session_id", "asset_code", "barcode",
        "description", "status", "scanned_at",
        "region", "city", "building",
    ]
    ws2.append(headers2)

    items = InventoryItem.objects.select_related(
        "session", "asset",
        "asset__region", "asset__city", "asset__building"
    )

    for item in items:
        ws2.append([
            item.session.id,
            item.asset.asset_code if item.asset else "",
            item.barcode,
            item.asset.description if item.asset else "",
            item.status,
            item.scanned_at.strftime("%Y-%m-%d %H:%M") if item.scanned_at else "",
            item.asset.region.name if item.asset and item.asset.region else "",
            item.asset.city.name if item.asset and item.asset.city else "",
            item.asset.building.name if item.asset and item.asset.building else "",
        ])

    for cell in ws2[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # ============================================================
    # Sheet 3 — المواقع
    # ============================================================
    ws3 = wb.create_sheet(title="Locations")

    headers3 = [
        "type", "region", "city", "building"
    ]
    ws3.append(headers3)

    for region in Region.objects.all():
        ws3.append(["region", region.name, "", ""])

    for city in City.objects.select_related("region"):
        ws3.append(["city", city.region.name, city.name, ""])

    for building in Building.objects.select_related("city", "city__region"):
        ws3.append([
            "building",
            building.city.region.name,
            building.city.name,
            building.name
        ])

    for cell in ws3[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # ============================================================
    # Sheet 4 — جميع الأصول
    # ============================================================
    ws4 = wb.create_sheet(title="Assets")

    headers4 = [
        "asset_code", "barcode", "old_barcode",
        "description", "main_category", "type",
        "sub_category", "region", "city", "building",
        "status", "condition",
        "custodian_number", "custodian_name", "custodian_type",
        "created_at", "created_by_username"
    ]
    ws4.append(headers4)

    assets = Asset.objects.select_related("region", "city", "building")

    for asset in assets:
        ws4.append([
            asset.asset_code,
            asset.barcode,
            asset.old_barcode,
            asset.description,
            asset.main_category,
            asset.type,
            asset.sub_category,
            asset.region.name if asset.region else "",
            asset.city.name if asset.city else "",
            asset.building.name if asset.building else "",
            asset.status,
            asset.condition,
            asset.custodian_number,
            asset.custodian_name,
            asset.custodian_type,
            asset.created_at.strftime("%Y-%m-%d") if asset.created_at else "",
            asset.created_by_username,
        ])

    for cell in ws4[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # ============================================================
    # تحميل الملف النهائي
    # ============================================================
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="full_inventory_backup.xlsx"'

    wb.save(response)
    return response
