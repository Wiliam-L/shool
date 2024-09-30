from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import uuid
from django.http import JsonResponse
from django.views import View
from .serializers import GroupSerializer, UserSerializer, CustomTokenObtainPairSerializer, UserShortSerailizer
from django.contrib.auth.models import Group, User
from rest_framework import viewsets, generics, status, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser
from apps.tutor.models import Tutor
from apps.administrator.namesGroup import AdminNames
from .serializers import EmailVerification, EmailVerificationSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SendEmailCodeConfirmation(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = self.request.data.get('email')
        if not email:
            return Response({'message': 'correo obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'message': 'No se encontró el usuario'
            }, status=status.HTTP_404_NOT_FOUND)

        existing_verification = EmailVerification.objects.filter(user=user).first()
        code = uuid.uuid4()
        expiration_date = timezone.now() + timedelta(minutes=10)

        if existing_verification:
            if existing_verification.is_code_valid():
                return Response({'message': 'Un código de verificación ya ha sido enviado y es válido.'}, 
                    status=status.HTTP_400_BAD_REQUEST)

            existing_verification.code = code
            existing_verification.expiration_date = expiration_date
            existing_verification.verificated = False
            existing_verification.save()
        else:            
            existing_verification = EmailVerification.objects.create(user=user, code=code, expiration_date=expiration_date)
        
        self.send_verification_email(user, code)
        return Response({"success": f"Código de verificación enviado: {code}"}, status=status.HTTP_200_OK)


    def send_verification_email(self, user, code):
        subject = 'Verificación de correo electrónico'
        message = f'Tu código de verificación es: {code} \nexpira en 10 minutos'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            raise serializers.ValidationError({'error': f'Error al enviar el correo: {str(e)}'})
        
class ConfirmCodeEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not email:
            return Response({'error': 'El correo es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        

        try:
            user=User.objects.get(email=email)
            verification = EmailVerification.objects.get(user=user)

            if verification.is_code_valid() and not verification.verificated:
                if str(code) == str(verification.code):
                    user.set_password(new_password)
                    user.save()
                    
                    verification.verificated=True
                    verification.save()
                    return Response({'correcto': 'contraseña actualizada'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'codigo inválido'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'message': 'Código inválido o ha expirado.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except EmailVerification.DoesNotExist:
            return Response({'message': 'No se encontró el registro de verificación.'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'message': 'No se encontó el usuario'}, status=status.HTTP_404_NOT_FOUND)

class UserShortListApiView(generics.ListAPIView):
    """
    administrador: solo lectura para usuarios
    """
    queryset = User.objects.all()
    serializer_class = UserShortSerailizer

class UserViewSet(viewsets.ModelViewSet):
    """
    administrador: CRUD de usuarios
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error inesperado: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        if user.is_superuser and User.objects.filter(is_superuser=True).count() == 1:
            return Response({'error': 'No se puede eliminar el único usuario administrador'}, status=status.HTTP_400_BAD_REQUEST)

        ADMIN_NAME_SET = {name for name in AdminNames()}
        if user.groups.filter(name__iexact=ADMIN_NAME_SET).exists() and User.objects.filter(groups__name__iexact="admin").count() == 1:
            return Response(
                {'error': 'No se puede eliminar el único usuario del grupo Admin.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        if Tutor.objects.filter(user=user).exists():
            return Response(
                {'error': 'No se puede eliminar el usuario porque está asociado a un tutor.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


        return super().destroy(request, *args, **kwargs)

#grupos
class GroupView(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')

        if Group.objects.filter(name=name).exists():
            return Response({'error': 'Grupo existente'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def destroy(self, request, *args, **kwargs):
            group = self.get_object()

            # Verificamos si hay usuarios asociados al grupo
            if group.user_set.exists():
                return Response(
                    {"error": "No se puede eliminar el grupo porque está siendo utilizado por uno o más usuarios."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Si no hay usuarios asociados, procedemos con la eliminación
            return super().destroy(request, *args, **kwargs)
    
class CreateUserView(View):
    def post(self, request):
        username = 'wlopez'
        email = 'admin@example.com'
        password = '123asdfgna'
        
        # Verifica si el superusuario ya existe
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'El superusuario ya existe.'}, status=400)
        
        # Crea el grupo si no existe
        group, created = Group.objects.get_or_create(name='admin')

        # Crea el superusuario
        user = User(
            username=username,
            email=email,
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        user.set_password(password)
        user.save()
        user.groups.add(group)
        
        return JsonResponse({'message': 'Superusuario creado y agregado al grupo.'}, status=201)
