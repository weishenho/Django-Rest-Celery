from django.db import models

# Create your models here.
class Total_files(models.Model):
    total_files = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)