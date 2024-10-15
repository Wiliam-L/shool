from django.urls import path
from .views import ShowTeacherListApiView, ShowCourseListApiView, ShowTutorListApiView, ShowNotaListApiView

urlpatterns = [
    path('showteacher/', ShowTeacherListApiView.as_view(), name="showteacher"),
    path('showcourse/', ShowCourseListApiView.as_view(), name="showcourse"),
    path('showtutor/', ShowTutorListApiView.as_view(), name="showtutor"),
    path('shownote/', ShowNotaListApiView.as_view(), name="shownote")
]