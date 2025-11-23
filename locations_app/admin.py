from django.contrib import admin
from .models import RegionGroup, Region, City, Building

# ============================
#     الإقليم (RegionGroup)
# ============================
@admin.register(RegionGroup)
class RegionGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# ============================
#           المناطق
# ============================
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group')
    list_filter = ('group',)
    search_fields = ('name', 'group__name')


# ============================
#           المدن
# ============================
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region')
    list_filter = ('region', 'region__group')
    search_fields = ('name', 'region__name', 'region__group__name')


# ============================
#          المباني
# ============================
@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')
    list_filter = ('city', 'city__region', 'city__region__group')
    search_fields = (
        'name',
        'city__name',
        'city__region__name',
        'city__region__group__name'
    )
