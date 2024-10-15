from django.urls import path, include
from .views import TeacherApiView, CoursesApiView, NoteStudentApiView, ShowStudentsApiview

urlpatterns = [
    path('teacher/', TeacherApiView.as_view()),
    path('courses/', CoursesApiView.as_view(), name='courses'),
    path('note/', NoteStudentApiView.as_view(), name='students-courses'),
    path('students/', ShowStudentsApiview.as_view(), name='students'),
]