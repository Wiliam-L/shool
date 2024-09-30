from django.core.exceptions import ValidationError
from django.db import models
from apps.student.models import Student

def validate_nota(value):
    if value < 0 or value > 100:
        raise ValidationError('La nota debe estar entre 0 y 100.')


class Note(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey('course.Course', on_delete=models.PROTECT)
    teacher = models.ForeignKey('teacher.Teacher', on_delete=models.PROTECT)
    note = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_nota])
    status_note = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta: db_table = 'note'

    def __str__(self):
        return f"{self.student.name} - {self.course.name}: {'Aprobado' if self.status_note else 'No aprobado'}"


