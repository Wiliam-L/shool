from django.urls import path
from .views import ShowTeacherListApiView, ShowCourseListApiView, ShowCourseAssignmentListApiView, ShowTutorListApiView, ShowNotaListApiView

urlpatterns = [
    path('showteacher/', ShowTeacherListApiView.as_view(), name="showteacher"),
    path('showcourse/', ShowCourseListApiView.as_view(), name="showcourse"),
    path('showassignament/', ShowCourseAssignmentListApiView.as_view(), name="showassignament"),
    path('showtutor/', ShowTutorListApiView.as_view(), name="showtutor"),
    path('shownote/', ShowNotaListApiView.as_view(), name="shownote")
]