from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CurseViewSet

router = DefaultRouter()
router.register(r'curse', CurseViewSet, basename='curse')

urlpatterns = [
    path('', include(router.urls))
]