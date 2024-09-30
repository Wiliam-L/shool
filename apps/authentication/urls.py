from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupView, UserViewSet, UserShortListApiView

router = DefaultRouter()
router.register(r'group', GroupView, basename='group')
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('show-user/', UserShortListApiView.as_view(), name="show-user"),
]