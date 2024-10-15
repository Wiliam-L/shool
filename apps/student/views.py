from rest_framework.generics import ListAPIView 
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.note.serializers import NoteSerializers, Note
from apps.teacher.serializers import TeacherSerializer, Teacher
from apps.authentication.permissions import IsInGroup 
from apps.administrator import namesGroup
from apps.student.models import Student
from apps.course.serializers import TeacherCourseAssignment, CourseofStudent, Course
from apps.registration.serializers import CourseRegistration
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
            teacher = Teacher.objects.get(user=user)
        except Student.DoesNotExist:
            return Course.objects.none()
        
        course_registrations = CourseRegistration.objects.filter(teacher=teacher)
        if not course_registrations.exists():
            return Course.objects.none()
        
        # Obtener las asignaciones de cursos de los registros
        teacher_course_assignment = TeacherCourseAssignment.objects.filter(id__in=course_registrations.values_list('teacher_course_assignment', flat=True))
        teachers_ids = teacher_course_assignment.values_list('teacher_id', flat=True)
        
        return Teacher.objects.filter(id__in=teachers_ids).distinct()


class ShowCourseListApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = CourseofStudent
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.StudentNames()


    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return CourseRegistration.objects.none()
        
        course_registration = CourseRegistration.objects.filter(student=student)
        if not course_registration.exists():
            return CourseRegistration.objects.none()
        
        return course_registration
    


    
class ShowCourseAssignmentListApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.StudentNames()

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

