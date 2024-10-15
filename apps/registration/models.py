from django.db import models
from apps.student.models import Student
from apps.course.models import TeacherCourseAssignment
from apps.grade.models import Grade
from apps.section.models import Section

class CourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    teacher_course_assignment = models.ManyToManyField(TeacherCourseAssignment)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'course_registration'

    
    def __str__(self):
        return f"{self.student.name} - {self.teacher_course_assignment} - Sección {self.teacher_course_assignment}"
