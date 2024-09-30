from rest_framework.generics import ListAPIView 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from apps.note.serializers import NoteSerializers, Note
from apps.teacher.serializers import TeacherSerializer, Teacher
from apps.authentication.permissions import IsInGroup 
from apps.administrator import namesGroup
from apps.student.models import Student
from apps.course.serializers import Course, CourseSerializer
from apps.registration.serializers import CourseRegistration, ShortCourseRegistrationSerializer
from apps.tutor.serializers import Tutor, ShortTutorSerializer
from apps.note.serializers import Note, ShortNoteSerializer

class ShowTeacherListApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = TeacherSerializer
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.StudentNames()

    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Teacher.objects.none()
        
        return Teacher.objects.filter(courseregistration__student=student)

class ShowCourseListApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = CourseSerializer
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.StudentNames()

    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Course.objects.none()
        
        return Course.objects.filter(courseregistration__student=student)
    
class ShowCourseAssignmentListApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.StudentNames()
    serializer_class = ShortCourseRegistrationSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist: return CourseRegistration.objects.none()

        return CourseRegistration.objects.filter(student=student)

class ShowTutorListApiView(ListAPIView): 
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.StudentNames()
    serializer_class = ShortTutorSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist: return Student.objects.none()

        return Tutor.objects.filter(id=student.tutor.id)

class ShowNotaListApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.StudentNames()
    serializer_class = ShortNoteSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist: return Student.objects.none()

        return Note.objects.filter(student=student)
    

#ver nota de los cursos 
class AlumnoNotaListView(ListAPIView):
    """
    para alumnos -> Read
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializers

