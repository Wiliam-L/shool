from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import NoteSerializers
from .models import Nota
from apps.registration.models import Matricula

class NotaView(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NoteSerializers
    
    def create(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        teacher_id = request.data.get('teacher_id')
        curse_id = request.data.get('curse_id')

        try:
            if not Matricula.objects.filter(student=student_id).exists():
                return Response({
                    'error': 'El alumno no esta asignado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not Matricula.objects.filter(teacher=teacher_id).exists():
                return Response({
                    'error': 'profesor invalido'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not Matricula.objects.filter(curse=curse_id).exists():
                return Response({
                    'error': 'curso invalido'
                }, status=status.HTTP_400_BAD_REQUEST)

            
            serializer = NoteSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': 'Ocurrió un error al procesar la solicitud.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
