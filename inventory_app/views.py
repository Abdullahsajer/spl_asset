from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from locations_app.models import Region, City, Building
from assets_app.models import Asset
from .models import InventorySession, InventoryItem


@login_required
def start_session_view(request):
    """
    منطق بدء جلسة جرد:
    - التحقق من المدخلات
    - إنشاء جلسة جديدة
    - تحميل الأصول التابعة للمبنى
    - إنشاء InventoryItem لكل أصل
    - تحويل الموظف إلى شاشة المسح المستمر
    """

    regions = Region.objects.all().order_by("name")
    cities = City.objects.all().order_by("name")
    buildings = Building.objects.all().order_by("name")

    if request.method == "POST":
        region_id = request.POST.get("region")
        city_id = request.POST.get("city")
        building_id = request.POST.get("building")

        # تحقق من أن جميع الخيارات موجودة
        if not (region_id and city_id and building_id):
            return render(request, "inventory_app/start_session.html", {
                "regions": regions,
                "cities": cities,
                "buildings": buildings,
                "error": "الرجاء اختيار المنطقة والمدينة والمبنى."
            })

        region = get_object_or_404(Region, id=region_id)
        city = get_object_or_404(City, id=city_id)
        building = get_object_or_404(Building, id=building_id)

        # 1) إنشاء جلسة جديدة
        session = InventorySession.objects.create(
            employee=request.user,
            region=region,
            city=city,
            building=building,
            status="in_progress"
        )

        # 2) تحميل أصول المبنى
        assets = Asset.objects.filter(
            region=region,
            city=city,
            building=building
        )

        # 3) إنشاء InventoryItem لكل أصل
        for asset in assets:
            InventoryItem.objects.create(
                session=session,
                asset=asset,
                barcode=asset.barcode,
                status="missing",   # الحالة الافتراضية
            )

        # 4) التحويل لصفحة المسح المستمر
        return redirect("inventory_app:live_scan", session_id=session.id)

    return render(request, "inventory_app/start_session.html", {
        "regions": regions,
        "cities": cities,
        "buildings": buildings
    })


@login_required
def live_scan_view(request, session_id):
    """
    عرض شاشة المسح المستمر + تحميل عناصر الجلسة
    """
    session = get_object_or_404(InventorySession, id=session_id)
    items = InventoryItem.objects.filter(session=session).select_related("asset")

    return render(request, "inventory_app/session_live_scan.html", {
        "session": session,
        "items": items
    })
