from rest_framework import serializers
from django.db import transaction, IntegrityError
from .models import Tutor
from django.contrib.auth.models import User
from apps.administrator.namesGroup import TutorNames

class ShortTutorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Tutor
        fields = ['name', 'phone', 'address','user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.user:
            representation['user'] = {'email': instance.user.email}
        
        return representation



class TutorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False) 
    class Meta:
        model = Tutor
        fields = ['id', 'name', 'phone', 'address', 'user', 'create_date', 'update_date']
    
        extra_kwargs = {
            'name': {'required': True},
            'phone': {'required': True},
            'user': {'required': True},
            'address': {'required': True}
        }
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        
        if instance.user: representation['user'] = {instance.user.email, instance.user.username}
        representation['create_date'] = instance.create_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites
        return representation
    
    def __init__(self, *args, **kwargs):
        super(TutorSerializer, self).__init__(*args, **kwargs)
        
        if self.instance:
            for field in ['name', 'phone', 'user', 'address']:
                self.fields[field].required = False
                self.fields[field].allow_blank = True
 

    def validate(self, data):
        instance = self.instance
        name = data.get('name')
        user = data.get('user')
        

        if not instance:
            try:
                groupname = user.groups.first().name if user.groups.exists() else None                
            except Exception as e: 
                raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})
            
            if name and Tutor.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError({"Error": "tutor '{name}' ya existente"})

            if not groupname:
                raise serializers.ValidationError(f"El usuario no pertenece a ningún grupo.")

            if groupname.lower() not in {name.lower() for name in TutorNames()}:
                raise serializers.ValidationError(f"El grupo no es correcto para este usuario. Se encontró: {groupname}")

            if Tutor.objects.filter(user=user).exists():
                raise serializers.ValidationError(f"El usuario ya está asignado a otro tutor.")

        else:
            #validamos si se esta cambian el nombre, que este nuevo nombre no exista ya en la db
            if name and Tutor.objects.filter(name__iexact=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"Error": "tutor '{name}' ya existente"})

            #validar nuevo usuario
            if 'user' in data and instance.user != user:
                groupname = user.groups.first().name if user.groups.exists() else None

                if not groupname:
                    raise serializers.ValidationError(f"El usuario no pertenece a ningún grupo.")
                
                TUTOR_NAMES_SET = {name.lower() for name in TutorNames()}
                if groupname.lower() not in TUTOR_NAMES_SET:
                    raise serializers.ValidationError(f"El grupo no es correcto para este usuario. Se encontró: {groupname}")

            if Tutor.objects.filter(user=user).exclude(id=instance.id).exists():
                raise serializers.ValidationError(f"El usuario ya está asignado a otro tutor.")


        return data

    @transaction.atomic
    def create(self, validate_data):
        validate_data.pop('userType', None)
        
        try:
            tutor = Tutor.objects.create(**validate_data)
            tutor.save()
            return tutor
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})
