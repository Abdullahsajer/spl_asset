from django.db import models
from django.contrib.auth.models import User
from locations_app.models import Region, City, Building
from assets_app.models import Asset


class InventorySession(models.Model):

    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('in_progress', 'جارية'),
        ('submitted_to_supervisor', 'مقدمة للمشرف'),
        ('supervisor_under_review', 'تحت مراجعة المشرف'),
        ('supervisor_approved', 'معتمدة من المشرف'),
        ('supervisor_rejected', 'مرفوضة من المشرف'),
        ('admin_approved', 'معتمدة نهائياً'),
        ('cancelled', 'ملغاة'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory_sessions", verbose_name="موظف الجرد")
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_sessions", verbose_name="المشرف")

    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, verbose_name="المنطقة")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name="المدينة")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, verbose_name="المبنى")

    start_time = models.DateTimeField(auto_now_add=True, verbose_name="وقت بدء الجلسة")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="وقت انتهاء الجلسة")

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")

    employee_comment = models.TextField(blank=True, null=True, verbose_name="ملاحظات الموظف")
    supervisor_comment = models.TextField(blank=True, null=True, verbose_name="ملاحظات المشرف")
    admin_comment = models.TextField(blank=True, null=True, verbose_name="ملاحظات مدير النظام")

    class Meta:
        verbose_name = "جلسة جرد"
        verbose_name_plural = "جلسات الجرد"

    def __str__(self):
        return f"جلسة {self.id} - {self.employee.username}"


class InventoryItem(models.Model):

    STATUS_CHOICES = [
        ('found', 'موجود'),
        ('missing', 'مفقود'),
        ('newly_added', 'مضاف جديد'),
    ]

    session = models.ForeignKey(InventorySession, on_delete=models.CASCADE, related_name="items", verbose_name="جلسة الجرد")
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الأصل")

    barcode = models.CharField(max_length=100, verbose_name="الباركود")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="حالة الجرد")
    scanned_at = models.DateTimeField(blank=True, null=True, verbose_name="وقت المسح")

    added_manually = models.BooleanField(default=False, verbose_name="أضيف يدوياً")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تفصيل جرد"
        verbose_name_plural = "تفاصيل الجرد"

    def __str__(self):
        return f"{self.barcode} - {self.get_status_display()}"
