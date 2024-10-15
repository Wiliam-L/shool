from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentListApiView, ShowCoursesApiView, ShowNotesApiView, ShowTeachersApiView

router = DefaultRouter()

urlpatterns = [
    path('student/', StudentListApiView.as_view(), name="tutor-student"),
    path('courses/', ShowCoursesApiView.as_view(), name='courses-students'),
    path('notes/', ShowNotesApiView.as_view(), name='notes-students'),
    path('teacher/', ShowTeachersApiView.as_view(), name='teacher-students')
]