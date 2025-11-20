from django.db import models

class ImportLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    table_name = models.CharField(max_length=200)
    rows_count = models.IntegerField()
    mode = models.CharField(max_length=20)  # add / replace
    status = models.CharField(max_length=20)  # success / failed
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.table_name} - {self.timestamp}"
