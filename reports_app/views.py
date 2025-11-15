from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from assets_app.models import Asset
from inventory_app.models import InventorySession, InventoryItem
from locations_app.models import Region, City, Building
from django.http import JsonResponse


# ======================================================
#     الصفحة الرئيسية للتقارير
# ======================================================
@login_required
def reports_home_view(request):

    total_assets = Asset.objects.count()
    total_sessions = InventorySession.objects.count()

    scanned = InventoryItem.objects.filter(status="found").count()
    missing = InventoryItem.objects.filter(status="missing").count()
    new = InventoryItem.objects.filter(status="new").count()

    context = {
        "total_assets": total_assets,
        "total_sessions": total_sessions,
        "total_scanned": scanned,
        "total_missing": missing,
        "total_new": new,
    }

    return render(request, "reports_app/reports_home.html", context)


# ======================================================
#     تقرير حالة مبنى
# ======================================================
@login_required
def building_status_report_view(request):

    buildings = Building.objects.select_related(
        "city", "city__region"
    ).all()

    report_data = []

    for b in buildings:
        # إجمالي الأصول في المبنى
        total = Asset.objects.filter(building=b).count()

        # المجرود
        scanned = InventoryItem.objects.filter(
            asset__building=b,
            status="found"
        ).count()

        # المفقود
        missing = InventoryItem.objects.filter(
            asset__building=b,
            status="missing"
        ).count()

        # الجديد
        new = InventoryItem.objects.filter(
            asset__building=b,
            status="new"
        ).count()

        # غير المجرودين
        not_scanned = total - (scanned + missing + new)

        report_data.append({
            "region": b.city.region.name,
            "city": b.city.name,
            "building": b.name,
            "total": total,
            "scanned": scanned,
            "missing": missing,
            "new": new,
            "not_scanned": not_scanned,
        })

    return render(request, "reports_app/building_status_report.html", {
        "data": report_data
    })


# ======================================================
#     تقرير حالة الجلسات
# ======================================================
@login_required
def sessions_status_report_view(request):

    sessions = InventorySession.objects.select_related(
        "employee", "region"
    ).all()

    counts = {
        "total": sessions.count(),
        "completed": sessions.filter(status="completed").count(),
        "approved": sessions.filter(status="supervisor_approved").count(),
        "rejected": sessions.filter(status="supervisor_rejected").count(),
        "under_review": sessions.filter(status="supervisor_under_review").count(),
        "draft": sessions.filter(status="draft").count(),
    }

    return render(request, "reports_app/sessions_status_report.html", {
        "counts": counts,
        "sessions": sessions,
    })


# ======================================================
#     التقرير الختامي الشامل للأصول
# ======================================================
@login_required
def summary_assets_report_view(request):

    total_assets = Asset.objects.count()

    scanned = InventoryItem.objects.filter(status="found").count()
    missing = InventoryItem.objects.filter(status="missing").count()
    new_added = InventoryItem.objects.filter(status="new").count()

    # حساب غير المجرود
    not_scanned = total_assets - (scanned + missing + new_added)

    # أداء المناطق
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

    context = {
        "total_assets": total_assets,
        "scanned": scanned,
        "missing": missing,
        "new_added": new_added,
        "not_scanned": not_scanned,
        "region_stats": region_stats,
    }

    return render(request, "reports_app/summary_assets_report.html", context)


# ================================
# AJAX – إرجاع المدن حسب المنطقة
# ================================
@login_required
def get_cities_ajax(request, region_id):
    cities = City.objects.filter(region_id=region_id).values("id", "name")
    return JsonResponse(list(cities), safe=False)

# ================================
# AJAX – إرجاع المباني حسب المدينة
# ================================
@login_required
def get_buildings_ajax(request, city_id):
    buildings = Building.objects.filter(city_id=city_id).values("id", "name")
    return JsonResponse(list(buildings), safe=False)