from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.authentication.permissions import IsInGroup
from .models import Teacher
from .serializers import TeacherSerializer
from rest_framework.generics import ListAPIView
from apps.administrator import namesGroup
from apps.course.serializers import Course, TeacherCourseAssignment
from apps.registration.serializers import CourseRegistration
from apps.teacher.serializers import TeacherSerializer, TeacherOfCourseAssignmentSerializer
from apps.student.serializers import Student, StudentShortSerializer
from apps.note.serializers import Note, NoteSerializers

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
    serializer_class = TeacherOfCourseAssignmentSerializer
    allowed_groups = namesGroup.TeacherNames()

    def get_queryset(self):
        user = self.request.user
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            return TeacherCourseAssignment.objects.none()
        
        teacher_course_assignment = TeacherCourseAssignment.objects.filter(teacher=teacher)
        return teacher_course_assignment
    

class ShowStudentCoursesApiView(ListAPIView):
    """
    El profesor puede ver los alumnos asignados
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    serializer_class = Course
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

        teacher_assignments = TeacherCourseAssignment.objects.filter(teacher=teacher)
        return Student.objects.filter(courseregistration__teacher_course_assignment__in=teacher_assignments).distinct()

class NoteStudentApiView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInGroup]
    allowed_groups = namesGroup.TeacherNames()
    serializer_class = NoteSerializers

    def get_queryset(self):
        user=self.request.user
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist: Note.objects.none()

        teacher_assignments = TeacherCourseAssignment.objects.filter(teacher=teacher)
        return Note.objects.filter(student__courseregistration__teacher_course_assignment__in=teacher_assignments).distinct()
    


