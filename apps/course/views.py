from rest_framework import viewsets
from .serializers import CourseSerializer, CourseScheduleSerializer, TeacherCourseAssignmentSerializer
from .models import Course, CourseSchedule

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseScheduleViewSet(viewsets.ModelViewSet):
    queryset = CourseSchedule.objects.all()
    serializer_class = CourseScheduleSerializer
    