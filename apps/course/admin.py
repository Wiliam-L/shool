from django.contrib import admin
from .models import Course, CourseSchedule, TeacherCourseAssignment

# Register your models here.
admin.site.register(Course)
admin.site.register(CourseSchedule)
admin.site.register(TeacherCourseAssignment)