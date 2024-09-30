from django.db import models
from apps.teacher.models import Speciality

class Level(models.Model):
    name = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'level'
    
    def __str__(self): return self.name

class Course(models.Model):
    name = models.CharField(max_length=255)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'course'
    
    def __str__(self): return f"{self.name}"

