from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Asset


@login_required
def assets_list_view(request):
    """
    عرض قائمة الأصول مع إمكانية التصفية مستقبلاً.
    """
    assets = Asset.objects.select_related("region", "city", "building").all().order_by("asset_code")
    context = {
        "assets": assets,
    }
    return render(request, "assets_app/assets_list.html", context)


@login_required
def asset_detail_view(request, asset_id):
    """
    عرض تفاصيل أصل واحد.
    """
    asset = get_object_or_404(Asset, id=asset_id)
    context = {
        "asset": asset,
    }
    return render(request, "assets_app/asset_detail.html", context)
