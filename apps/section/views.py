from rest_framework import viewsets
from .serializers import SectionSerializer
from .models import Section

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
