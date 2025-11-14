from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Asset


@login_required
def assets_list_view(request):
    assets = Asset.objects.select_related("region", "city", "building").all().order_by(
        "asset_code"
    )
    return render(request, "assets_app/assets_list.html", {"assets": assets})


@login_required
def asset_detail_view(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    return render(request, "assets_app/asset_detail.html", {"asset": asset})
