from rest_framework import serializers
from django.db import IntegrityError
from .models import Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'description', 'code', 'creation_date', 'update_date']

        extra_kwargs = {
            'name': {'required': True},
            'description': {'required': True},
            'code': {'required': True},
            'creation_date': {'required': True},
            'update_date': {'required': True}
        }

    def __init__(self, *args, **kwargs):
        super(GradeSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in ['name', 'description', 'code', 'creation_date', 'update_date']:
                self.fields[field].required = False
                self.fields[field].allow_blank = True

    def validate(self, data):
        instance = self.instance
        name = data.get('name')
        code = data.get('code')

        if not instance:
            if name and Grade.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError(f'El grado: {name} ya existe.')

            if code and Grade.objects.filter(code__iexact=code).exists():
                raise serializers.ValidationError(f'El código: {code} ya existe.')
        else:
            if name and Grade.objects.filter(name__iexact=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError(f'{name} ya existe.')
            
            if code and Grade.objects.filter(code__iexact=code).exclude(id=instance.id).exists():
                raise serializers.ValidationError(f'{code} ya existe. ')
            
        return data
    
    def create(self, validated_data):
        try:
            grade = Grade.objects.create(**validated_data)
            grade.save()
            return grade
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad'+str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado'+ str(e)})