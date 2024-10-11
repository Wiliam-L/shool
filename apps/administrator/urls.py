from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentShortListApiView, StudentNoteViewSet, RegistrationStudentViewSet, TeacherViewSet, SpecialityViewSet, TutorViewSet, CourseViewSet, LevelViewSet, GradeViewSet

router = DefaultRouter()
router.register(r'course', CourseViewSet, basename='course')
router.register(r'student', StudentViewSet, basename='student')
router.register(r'student-registration', RegistrationStudentViewSet, basename='student-registration')
router.register(r'student-note', StudentNoteViewSet, basename="student-note")
router.register(r'teacher', TeacherViewSet, basename='teacher')
router.register(r'speciality', SpecialityViewSet, basename='speciality')
router.register(r'tutor', TutorViewSet, basename='tutor')
router.register(r'level', LevelViewSet, basename='level')


urlpatterns = [
    path('', include('apps.authentication.urls')),
    path('short-student', StudentShortListApiView.as_view(), name="short-student"),
    path('section/', include('apps.section.urls')),
    path('', include(router.urls))
]

