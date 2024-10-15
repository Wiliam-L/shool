from django.db import models
from apps.teacher.models import Speciality, Teacher
from apps.grade.models import Grade
from apps.section.models import Section


class CourseSchedule(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'course_schedule'
    
    def __str__(self):
        return f"inicio: {self.start_time} - end: {self.end_time}"

class Course(models.Model):
    name = models.CharField(max_length=255)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'course'
    
    def __str__(self): return f"{self.name}"

class TeacherCourseAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'teacher_course_assignment'
        unique_together = ('course', 'grade', 'section', 'schedule')

    def __str__(self):
        return f"{self.course} - {self.teacher} ({self.grade} {self.section} : {self.schedule})"
    
