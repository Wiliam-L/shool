from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

router = DefaultRouter()
router.register(r'curse', CourseViewSet, basename='curse')

urlpatterns = [
    path('', include(router.urls))
]