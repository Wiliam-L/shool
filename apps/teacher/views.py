from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.authentication.permissions import IsInGroup
from .models import Teacher, Speciality
from .serializers import TeacherSerializer, SpecialitySerializer, CourseWithSectionSerializer
from rest_framework.generics import ListAPIView
from apps.administrator import namesGroup
from apps.course.serializers import Course, CourseSerializer
from apps.registration.serializers import CourseRegistration, CourseRegistrationSerializer, ShortCourseRegistrationSerializer

from apps.student.serializers import Student, StudentShortSerializer, StudentForTeacher, StudentAllSerializer

class TeacherApiView(ListAPIView):
    """
    El profesor puede ver su información
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    serializer_class = TeacherSerializer
    allowed_groups = namesGroup.TeacherNames()
    
    def get_queryset(self):
        user = self.request.user
        try:
            teacher = Teacher.objects.filter(user=user)
        except Teacher.DoesNotExist:
            return Teacher.objects.none()
        return teacher

class CoursesApiView(ListAPIView):
    """
    El profesor puede ver los cursos que tiene asignados
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    serializer_class = CourseWithSectionSerializer
    allowed_groups = namesGroup.TeacherNames()

    def get_queryset(self):
        user = self.request.user
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            return Teacher.objects.none()

        return Course.objects.filter(courseregistration__teacher=teacher).distinct()

class ShowStudentCoursesApiView(ListAPIView):
    """
    El profesor puede ver los alumnos asignados
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    serializer_class = ShortCourseRegistrationSerializer
    allowed_groups = namesGroup.TeacherNames()

    def get_queryset(self):
        user=self.request.user
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            return Teacher.objects.none()
        registrations = CourseRegistration.objects.filter(teacher=teacher)
        return registrations

class ShowStudentsApiview(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.TeacherNames()
    serializer_class = StudentShortSerializer

    def get_queryset(self):
        user=self.request.user
        try:
            teacher=Teacher.objects.get(user=user)
        except Teacher.DoesNotExist: return Teacher.objects.none()
        return Student.objects.filter(courseregistration__teacher=teacher)

class SpecialityViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.TeacherNames()
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer


