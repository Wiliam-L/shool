from django.db import transaction, IntegrityError
from django.db.models.functions import Lower
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status, serializers
from rest_framework.response import Response
from apps.student.serializers import Student, StudentAllSerializer, StudentShortSerializer
from apps.registration.serializers import CourseRegistration, CourseRegistrationSerializer
from apps.note.serializers import NoteSerializers, Note
from apps.tutor.serializers import Tutor, TutorSerializer
from apps.teacher.serializers import Teacher, Speciality, SpecialitySerializer, TeacherSerializer
from apps.course.serializers import CourseSerializer, Course, LevelSerializer, Level
from apps.grade.serializers import Grade, GradeSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser


class CourseViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

#Matricula alumnos
class RegistrationStudentViewSet(viewsets.ModelViewSet):
    """Administrador:  
    acceso completo - CRUD para manipular matriculas
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = CourseRegistration.objects.all()
    serializer_class = CourseRegistrationSerializer

#Alumno
class StudentViewSet(viewsets.ModelViewSet):
    """Administrador:
    acceso completo - CRUD para manipular alumnos
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Student.objects.all()
    serializer_class = StudentAllSerializer


class StudentShortListApiView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Student.objects.all()
    serializer_class = StudentShortSerializer

#nota alumno
class StudentNoteViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Note.objects.all()
    serializer_class = NoteSerializers

#tutor
class TutorViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer

# views.py
class TeacherViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class GradeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

#especialidad
class SpecialityViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer

    @transaction.atomic
    def create(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'nombre requerido'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SpecialitySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'error': 'Especialidad ya existe'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LevelViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    queryset = Level.objects.all()
    serializer_class = LevelSerializer



from django.http import HttpResponse


def home_page_view(request):
    return HttpResponse("Hello, World!")
