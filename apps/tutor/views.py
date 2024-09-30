from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.administrator import namesGroup
from apps.authentication.permissions import IsInGroup
from .models import Tutor
from apps.student.models import Student
from apps.student.serializers import StudentShortSerializer
from apps.registration.serializers import ShortCourseRegistrationSerializer, CourseRegistration
from apps.note.serializers import NoteSerializers, Note
from apps.teacher.serializers import ShortTeacherSerializer, TeacherSerializer, Teacher

class StudentListApiView(ListAPIView): 
    """Para tutor: 
    permission READ para ver alumnos a su cargo
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.TutorNames()
    serializer_class = StudentShortSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            tutor = Tutor.objects.get(user=user)
        except Tutor.DoesNotExist: return Tutor.objects.none()

        students = Student.objects.filter(tutor=tutor)
        return students
        
class ShowCoursesApiView(ListAPIView):
    """
    ver cursos de sus alumnos a cargo
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.TutorNames()
    serializer_class = ShortCourseRegistrationSerializer

    def get_queryset(self):
        user=self.request.user
        try:
            tutor = Tutor.objects.get(user=user)
        except: CourseRegistration.objects.none()

        students = Student.objects.filter(tutor=tutor)
        return CourseRegistration.objects.filter(student__in=students)

class ShowNotesApiView(ListAPIView):
    permission_classes = [IsInGroup]
    authentication_classes =[JWTAuthentication]
    allowed_groups = namesGroup.TutorNames()
    serializer_class = NoteSerializers

    def get_queryset(self):
        user = self.request.user
        try:
            tutor = Tutor.objects.get(user=user)
        except Note.DoesNotExist: return Note.objects.none()

        students = Student.objects.filter(tutor=tutor)
        return Note.objects.filter(student__in=students)

class ShowTeachersApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.TutorNames()
    serializer_class = TeacherSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            tutor = Tutor.objects.get(user=user)
        except Tutor.DoesNotExist: return Teacher.objects.none()
        students = Student.objects.filter(tutor=tutor)
        registrations = CourseRegistration.objects.filter(student__in=students)
        return Teacher.objects.filter(courseregistration__in=registrations).distinct()
        