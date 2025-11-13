from django.contrib import admin
from .models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'asset_code', 'barcode', 'description',
        'region', 'city', 'building',
        'main_category', 'type', 'sub_category',
        'status', 'condition'
    )
    list_filter = (
        'region', 'city', 'building',
        'main_category', 'type', 'status'
    )
    search_fields = (
        'asset_code', 'barcode', 'description',
        'custodian_name', 'custodian_number'
    )
