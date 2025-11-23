from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from locations_app.models import RegionGroup, Region, City, Building
from assets_app.models import Asset


# ======================================
#        نموذج جلسة الجرد
# ======================================
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
        ('completed', 'منتهية'),
    ]

    # الموظف الذي قام بالجرد
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inventory_sessions",
        verbose_name="موظف الجرد"
    )

    # المشرف
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="reviewed_sessions",
        verbose_name="المشرف"
    )

    # الإقليم
    region_group = models.ForeignKey(
        RegionGroup,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="الإقليم"
    )

    # المنطقة
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL,
        null=True, verbose_name="المنطقة"
    )

    # المدينة
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL,
        null=True, verbose_name="المدينة"
    )

    # المبنى
    building = models.ForeignKey(
        Building, on_delete=models.SET_NULL,
        null=True, verbose_name="المبنى"
    )

    # أوقات الجلسة
    start_time = models.DateTimeField(
        auto_now_add=True, verbose_name="وقت بدء الجلسة"
    )
    end_time = models.DateTimeField(
        null=True, blank=True,
        verbose_name="وقت انتهاء الجلسة"
    )

    # الحالة
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="الحالة"
    )

    # ملاحظات workflow
    employee_comment = models.TextField(
        blank=True, null=True, verbose_name="ملاحظات الموظف"
    )
    supervisor_comment = models.TextField(
        blank=True, null=True, verbose_name="ملاحظات المشرف"
    )
    admin_comment = models.TextField(
        blank=True, null=True, verbose_name="ملاحظات مدير النظام"
    )

    class Meta:
        verbose_name = "جلسة جرد"
        verbose_name_plural = "جلسات الجرد"

    def __str__(self):
        return f"جلسة {self.id} - {self.employee.username}"

    @property
    def items_count(self):
        return self.items.count()



# ======================================
#        تفاصيل الجرد لكل أصل
# ======================================
class InventoryItem(models.Model):

    STATUS_CHOICES = [
        ('found', 'موجود'),
        ('missing', 'مفقود'),
        ('new', 'أصل جديد'),
    ]

    session = models.ForeignKey(
        InventorySession,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="جلسة الجرد"
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="الأصل"
    )

    barcode = models.CharField(
        max_length=200,
        verbose_name="الباركود"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='missing',
        verbose_name="حالة الجرد"
    )

    scanned_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="وقت المسح"
    )

    added_manually = models.BooleanField(
        default=False,
        verbose_name="أضيف يدوياً"
    )

    notes = models.TextField(
        blank=True, null=True,
        verbose_name="ملاحظات"
    )

    class Meta:
        verbose_name = "تفصيل جرد"
        verbose_name_plural = "تفاصيل الجرد"

    def __str__(self):
        return f"{self.barcode} - {self.get_status_display()}"
