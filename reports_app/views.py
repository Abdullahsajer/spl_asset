from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse

from assets_app.models import Asset
from inventory_app.models import InventorySession, InventoryItem
from locations_app.models import Region, City, Building
from django.http import HttpResponseForbidden
from inventory_app.models import InventorySession


from .utils import generate_excel


# ======================================================
#     الصفحة الرئيسية للتقارير
# ======================================================
@login_required
def reports_home_view(request):

    total_assets = Asset.objects.count()
    total_sessions = InventorySession.objects.count()

    scanned = InventoryItem.objects.filter(status="found").count()
    missing = InventoryItem.objects.filter(status="missing").count()
    new_added = InventoryItem.objects.filter(status="new").count()

    context = {
        "total_assets": total_assets,
        "total_sessions": total_sessions,
        "total_scanned": scanned,
        "total_missing": missing,
        "total_new": new_added,
    }

    return render(request, "reports_app/reports_home.html", context)


# ======================================================
#     تقرير حالة المباني + فلاتر + تصدير Excel
# ======================================================
@login_required
def building_status_report_view(request):

    regions = Region.objects.all()

    selected_region = request.GET.get("region")
    selected_city = request.GET.get("city")
    selected_building = request.GET.get("building")

    buildings = Building.objects.select_related("city", "city__region").all()

    # تطبيق الفلاتر
    if selected_region:
        buildings = buildings.filter(city__region_id=selected_region)

    if selected_city:
        buildings = buildings.filter(city_id=selected_city)

    if selected_building:
        buildings = buildings.filter(id=selected_building)

    report_data = []

    for b in buildings:
        total = Asset.objects.filter(building=b).count()

        scanned = InventoryItem.objects.filter(
            asset__building=b, status="found"
        ).count()

        missing = InventoryItem.objects.filter(
            asset__building=b, status="missing"
        ).count()

        new_added = InventoryItem.objects.filter(
            asset__building=b, status="new"
        ).count()

        not_scanned = total - (scanned + missing + new_added)

        report_data.append({
            "region": b.city.region.name,
            "city": b.city.name,
            "building": b.name,
            "total": total,
            "scanned": scanned,
            "missing": missing,
            "new": new_added,
            "not_scanned": not_scanned,
        })

    # ========== تصدير Excel ==========
    if "export" in request.GET:
        headers = ["المنطقة", "المدينة", "المبنى", "إجمالي", "مجرود", "غير مجرود", "نسبة الإنجاز"]
        rows = [
            [
                row["region"],
                row["city"],
                row["building"],
                row["total"],
                row["scanned"],
                row["not_scanned"],
                round((row["scanned"] / row["total"] * 100), 1) if row["total"] else 0,
            ]
            for row in report_data
        ]

        return generate_excel(headers, rows, "building_status.xlsx")

    return render(request, "reports_app/building_status_report.html", {
        "data": report_data,
        "regions": regions,
        "cities": City.objects.all(),
        "buildings": Building.objects.all(),
        "selected_region": selected_region,
        "selected_city": selected_city,
        "selected_building": selected_building,
    })


# ======================================================
#     تقرير حالة الجلسات + تصدير Excel
# ======================================================
@login_required
def sessions_status_report_view(request):

    sessions = InventorySession.objects.select_related("employee", "region").all()

    counts = {
        "total": sessions.count(),
        "completed": sessions.filter(status="completed").count(),
        "approved": sessions.filter(status="supervisor_approved").count(),
        "rejected": sessions.filter(status="supervisor_rejected").count(),
        "under_review": sessions.filter(status="supervisor_under_review").count(),
        "draft": sessions.filter(status="draft").count(),
    }

    # ========== تصدير Excel ==========
    if "export" in request.GET:
        headers = ["رقم الجلسة", "الموظف", "المنطقة", "الحالة"]
        rows = [
            [
                s.id,
                s.employee.username if s.employee else "-",
                s.region.name if s.region else "-",
                s.get_status_display(),
            ]
            for s in sessions
        ]
        return generate_excel(headers, rows, "sessions_status.xlsx")

    return render(request, "reports_app/sessions_status_report.html", {
        "counts": counts,
        "sessions": sessions,
    })


# ======================================================
#     التقرير الختامي الشامل + تصدير Excel
# ======================================================
@login_required
def summary_assets_report_view(request):

    total_assets = Asset.objects.count()

    scanned = InventoryItem.objects.filter(status="found").count()
    missing = InventoryItem.objects.filter(status="missing").count()
    new_added = InventoryItem.objects.filter(status="new").count()

    not_scanned = total_assets - (scanned + missing + new_added)

    region_stats = Region.objects.annotate(
        assets_count=Count("cities__buildings__asset", distinct=True),
        scanned_count=Count(
            "cities__buildings__asset__inventoryitem",
            filter=Q(cities__buildings__asset__inventoryitem__status="found"),
            distinct=True
        ),
        missing_count=Count(
            "cities__buildings__asset__inventoryitem",
            filter=Q(cities__buildings__asset__inventoryitem__status="missing"),
            distinct=True
        ),
        new_count=Count(
            "cities__buildings__asset__inventoryitem",
            filter=Q(cities__buildings__asset__inventoryitem__status="new"),
            distinct=True
        )
    )

    # ========== تصدير Excel ==========
    if "export" in request.GET:
        headers = ["المنطقة", "إجمالي", "مجرود", "مفقود", "جديد", "غير مجرود"]
        rows = [
            [
                region.name,
                region.assets_count,
                region.scanned_count,
                region.missing_count,
                region.new_count,
                region.assets_count - region.scanned_count,
            ]
            for region in region_stats
        ]
        return generate_excel(headers, rows, "summary_assets.xlsx")

    return render(request, "reports_app/summary_assets_report.html", {
        "total_assets": total_assets,
        "scanned": scanned,
        "missing": missing,
        "new_added": new_added,
        "not_scanned": not_scanned,
        "region_stats": region_stats,
    })


# ======================================================
#     AJAX – إرجاع المدن حسب المنطقة
# ======================================================
@login_required
def get_cities_ajax(request, region_id):
    cities = City.objects.filter(region_id=region_id).values("id", "name")
    return JsonResponse(list(cities), safe=False)


# ======================================================
#     AJAX – إرجاع المباني حسب المدينة
# ======================================================
@login_required
def get_buildings_ajax(request, city_id):
    buildings = Building.objects.filter(city_id=city_id).values("id", "name")
    return JsonResponse(list(buildings), safe=False)


@login_required
def pending_sessions(request):

    # السماح فقط للمشرف والمدير
    user_groups = request.user.groups.values_list("name", flat=True)

    if not (request.user.is_superuser or "supervisors" in user_groups or "admins" in user_groups):
        return render(request, "403.html", status=403)

    # جلب الجلسات بانتظار المراجعة
    sessions = InventorySession.objects.filter(
        status="supervisor_under_review"
    ).select_related("employee", "region")

    return render(request, "reports_app/pending_sessions.html", {
        "sessions": sessions
    })


@login_required
def pending_sessions_view(request):
    sessions = InventorySession.objects.filter(status="supervisor_under_review")
    return render(request, "templates/pending_sessions.html", {"sessions": sessions})