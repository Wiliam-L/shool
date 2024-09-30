from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet

router = DefaultRouter()
router.register(r'grade', GradeViewSet, basename='grade')

urlpatterns = [
    path('ad/', include(router.urls))
]