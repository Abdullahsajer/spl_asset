from django.db import models
from locations_app.models import Region, City, Building

class Asset(models.Model):
    asset_code = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, unique=True)
    old_barcode = models.CharField(max_length=100, blank=True, null=True)

    description = models.TextField()

    # التصنيفات
    main_category = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=200)

    # الموقع
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)

    # بيانات إضافية
    status = models.CharField(max_length=50, default="فعال")
    condition = models.CharField(max_length=50, blank=True, null=True)

    custodian_number = models.CharField(max_length=50, blank=True, null=True)
    custodian_name = models.CharField(max_length=150, blank=True, null=True)
    custodian_type = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateField()
    created_by_username = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.asset_code} - {self.description[:30]}"
