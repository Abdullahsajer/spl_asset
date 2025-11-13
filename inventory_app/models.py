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

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory_sessions")
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_sessions")

    # الموقع المختار أثناء الجلسة
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')

    employee_comment = models.TextField(blank=True, null=True)
    supervisor_comment = models.TextField(blank=True, null=True)
    admin_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"جلسة {self.id} - {self.employee.username} - {self.building}"


class InventoryItem(models.Model):

    STATUS_CHOICES = [
        ('found', 'موجود'),
        ('missing', 'مفقود'),
        ('newly_added', 'مضاف جديد'),
    ]

    session = models.ForeignKey(InventorySession, on_delete=models.CASCADE, related_name="items")
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)

    barcode = models.CharField(max_length=100)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    scanned_at = models.DateTimeField(blank=True, null=True)

    added_manually = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.barcode} - {self.get_status_display()}"
