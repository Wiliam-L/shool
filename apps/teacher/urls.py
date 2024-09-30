from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherApiView, SpecialityViewSet, CoursesApiView, ShowStudentCoursesApiView, ShowStudentsApiview

router = DefaultRouter()
router.register(r'speciality', SpecialityViewSet, basename='speciality')

urlpatterns = [
    path('teacher/', TeacherApiView.as_view()),
    path('courses/', CoursesApiView.as_view(), name='courses'),
    path('students-courses/', ShowStudentCoursesApiView.as_view(), name='students-courses'),
    path('students/', ShowStudentsApiview.as_view(), name='students'),
    path('', include(router.urls))
]