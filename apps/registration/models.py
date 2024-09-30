from django.db import models
from apps.student.models import Student

class CourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    level = models.ForeignKey('course.Level', on_delete=models.PROTECT)
    course = models.ManyToManyField('course.Course')
    section = models.ForeignKey('section.Section', on_delete=models.PROTECT)
    teacher = models.ManyToManyField('teacher.Teacher')
    start_time = models.TimeField()
    end_time = models.TimeField()
    create_date = models.TimeField(auto_now_add=True)
    update_date = models.TimeField(auto_now=True)

    class Meta:
        db_table = 'course_registration'
    
    def __str__(self) -> str:
        return f"{self.student.name} - Sección {self.section.name} - Nivel {self.level}"