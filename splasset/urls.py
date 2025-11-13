from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # لوحة التحكم
    path('admin/', admin.site.urls),

    # ⭐ روابط التطبيقات
    path('accounts/', include('accounts_app.urls')),
    path('locations/', include('locations_app.urls')),
    path('assets/', include('assets_app.urls')),
    path('inventory/', include('inventory_app.urls')),
    path('reports/', include('reports_app.urls')),
]
