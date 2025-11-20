from django.contrib import admin
from .models import ImportLog

@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "table_name", "rows_count", "mode", "status")
    list_filter = ("table_name", "mode", "status")
    search_fields = ("table_name", "message")
