from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import Group
from django.db import IntegrityError
from .models import EmailVerification

class EmailVerificationSerializer(serializers.ModelSerializer):
    user=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = EmailVerification
        fields = ['user', 'code', 'expiration_date', 'verificated']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.user: representation['user'] = {instance.user.username, instance.user.email}

        return representation

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer): 
    group = serializers.CharField(write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        request_group = attrs.get('group')

        if not user.groups.filter(name__iexact=request_group).exists():
            raise serializers.ValidationError({"group": f"{user}, no es - {request_group}"})

        return data
    pass

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']
    

    def create(self, validated_data):
        name = validated_data.get('name')
        if Group.objects.filter(name=name).exists():
            raise serializers.ValidationError({"eror": "Ya existe un grupo con este nombre."})
            
        group = Group.objects.create(name=name)
        return group

class UserShortSerailizer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False)

    class Meta: 
        model = User
        fields = ['id', 'username', 'group']

    def to_representation (self, instance):
        representation  = super().to_representation(instance)
        representation['groups'] = [group.name for group in instance.groups.all()]
        return representation 

class UserSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'is_staff', 'is_superuser', 'is_active', 'email', 'first_name', 'last_name', 'group']
        extra_kwargs = {
            'password': {'write_only': True},  
            'username': {'required':True}, 
            'email': {'required': True},
            'is_active': {'required': True},
        }
    
    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            # Remover el requisito de los campos al actualizar
            for field in ['password', 'username', 'email', 'is_active']:
                self.fields[field].required = False
                self.fields[field].allow_blank = True  # Permitir campos vacíos si no son enviados

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Este correo ya está en uso.'})

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Este nombre de usuario ya está en uso.'})

        if first_name and last_name and User.objects.filter(first_name=first_name, last_name=last_name).exists():
            raise serializers.ValidationError({'first_name': 'El nombre completo ya está en uso.'})


        return data

    def create(self, validated_data):
        group = validated_data.pop('group', None)
        try:
            user = User.objects.create(
                username = validated_data['username'],
                email = validated_data['email'],
                is_staff = validated_data.get('is_staff', False),
                is_superuser = validated_data.get('is_superuser', False),
                is_active = validated_data.get('is_active', True),
                first_name = validated_data['first_name'],
                last_name = validated_data['last_name']   
            )

            password = validated_data.get('password')
            if password:
                user.set_password(password)

            if group:
                user.save()
                user.groups.add(group)


            return user
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})    
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})
        

    def update(self, instance, validated_data):
        group_id = validated_data.pop('group', None)

        # Actualiza atributos generales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Actualiza la contraseña si se proporciona
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        # Validación y actualización del grupo
        if str(group_id).lower() == "admin":
            if not validated_data.get('is_superuser', instance.is_superuser):
                raise serializers.ValidationError({'is_superuser': 'El usuario debe ser superusuario si está en el grupo Admin.'})
        else:
            if validated_data.get('is_superuser', instance.is_superuser):
                raise serializers.ValidationError({'is_superuser': 'El usuario no puede ser superusuario si no está en el grupo Admin.'})
                         
        instance.groups.set([group_id])
                
        instance.save()
        return instance


    def to_representation (self, instance):
        representation  = super().to_representation(instance)
        representation['groups'] = [group.name for group in instance.groups.all()]
        return representation 