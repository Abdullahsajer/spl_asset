from django.contrib import admin
from .models import InventorySession, InventoryItem

@admin.register(InventorySession)
class InventorySessionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'employee', 'region', 'city', 'building',
        'start_time', 'end_time', 'status'
    )
    list_filter = (
        'status', 'region', 'city', 'building', 'employee'
    )
    search_fields = (
        'id', 'employee__username', 'building__name'
    )


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        'barcode', 'session', 'asset',
        'status', 'scanned_at', 'added_manually'
    )
    list_filter = (
        'status', 'added_manually', 'session__building'
    )
    search_fields = (
        'barcode', 'asset__asset_code', 'asset__description'
    )
