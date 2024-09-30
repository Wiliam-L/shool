from rest_framework import viewsets
from .serializers import GradeSerializer
from .models import Grade

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    