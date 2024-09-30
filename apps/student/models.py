from django.db import models
from django.contrib.auth.models import User


class Student(models.Model): 
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=11)
    birthdate = models.DateField()
    address = models.CharField(max_length=255)
    emergency_contact = models.CharField(max_length=15)
    tutor = models.ForeignKey('tutor.Tutor', on_delete=models.PROTECT)
    creation_date = models.DateField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    suspended_student = models.BooleanField(default=False) 

    class Meta: db_table = "student"
    
    def __str__(self) -> str: return self.name
    
    @property
    def email(self): return self.user.email

