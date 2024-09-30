from django.db import models
from django.contrib.auth.models import User

class Speciality(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta: 
        db_table = "speciality"

    def __str__(self): return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    speciality = models.ManyToManyField(Speciality) 
    name = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=11)
    level = models.ManyToManyField('course.Level')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = "teacher"

    def __str__(self): return self.name
    
    @property
    def email(self): return self.user.email



