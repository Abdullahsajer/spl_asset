from django.db import models
from locations_app.models import Region, City, Building

class Asset(models.Model):
    asset_code = models.CharField(max_length=50, unique=True, verbose_name="رمز الأصل")
    barcode = models.CharField(max_length=100, unique=True, verbose_name="الباركود")
    old_barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="الباركود القديم")
    description = models.TextField(verbose_name="وصف الأصل")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="رقم الهاتف")


    # التصنيفات
    main_category = models.CharField(max_length=100, verbose_name="الفئة الرئيسية")
    type = models.CharField(max_length=100, verbose_name="النوع")
    sub_category = models.CharField(max_length=200, verbose_name="الفئة الفرعية")

    # الموقع
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, verbose_name="المنطقة")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name="المدينة")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, verbose_name="المبنى")

    # الحالة
    status = models.CharField(max_length=50, default="فعال", verbose_name="حالة الأصل")
    condition = models.CharField(max_length=50, blank=True, null=True, verbose_name="حالة الاستخدام")

    # العهدة
    custodian_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم صاحب العهدة")
    custodian_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="اسم صاحب العهدة")
    custodian_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="نوع العهدة")

    # التسجيل
    created_at = models.DateField(verbose_name="تاريخ الإدخال")
    created_by_username = models.CharField(max_length=100, verbose_name="المستخدم المدخل")

    class Meta:
        verbose_name = "أصل"
        verbose_name_plural = "الأصول"

    def __str__(self):
        return f"{self.asset_code} - {self.description[:20]}"
