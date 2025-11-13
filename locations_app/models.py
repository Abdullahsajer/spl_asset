from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.region} - {self.name}"


class Building(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="buildings")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.city.region} - {self.city} - {self.name}"
