from django.db import models
from django.contrib.auth.models import User
from locations_app.models import Region, RegionGroup

class Profile(models.Model):
    ROLE_CHOICES = [
        ('employees', 'موظف جرد'),
        ('supervisors', 'مشرف'),
        ('admins', 'مدير نظام'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="اسم المستخدم")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="الدور")

    # الإقليم (قد يكون أكثر من إقليم)
    region_groups = models.ManyToManyField(RegionGroup, blank=True, verbose_name="الأقاليم")

    # المناطق (قد يكون أكثر من منطقة)
    regions = models.ManyToManyField(Region, blank=True, verbose_name="المناطق")

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
