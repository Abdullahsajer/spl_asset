from django.db import models


# ======================================
#           جدول الأقاليم
# ======================================
class RegionGroup(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="اسم الإقليم"
    )

    class Meta:
        verbose_name = "إقليم"
        verbose_name_plural = "الأقاليم"

    def __str__(self):
        return self.name


# ======================================
#           جدول المناطق
# ======================================
class Region(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="اسم المنطقة"
    )

    # 🔥 ربط المنطقة بالإقليم
    group = models.ForeignKey(
    RegionGroup,
    on_delete=models.CASCADE,
    related_name="regions",
    verbose_name="الإقليم",
    null=True, blank=True   
    )

    class Meta:
        verbose_name = "منطقة"
        verbose_name_plural = "المناطق"

    def __str__(self):
        return f"{self.group} - {self.name}"


# ======================================
#           جدول المدن
# ======================================
class City(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="cities",
        verbose_name="المنطقة"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="اسم المدينة"
    )

    class Meta:
        verbose_name = "مدينة"
        verbose_name_plural = "المدن"

    def __str__(self):
        return f"{self.region} - {self.name}"


# ======================================
#           جدول المباني
# ======================================
class Building(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="buildings",
        verbose_name="المدينة"
    )
    name = models.CharField(
        max_length=150,
        verbose_name="اسم المبنى"
    )
    code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="كود المبنى"
    )

    class Meta:
        verbose_name = "مبنى"
        verbose_name_plural = "المباني"

    def __str__(self):
        return f"{self.city.region} - {self.city} - {self.name}"
