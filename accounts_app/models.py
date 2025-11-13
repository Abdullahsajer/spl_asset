from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('employee', 'موظف جرد'),
        ('supervisor', 'مشرف'),
        ('admin', 'مدير نظام'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="اسم المستخدم")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="الدور")

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
