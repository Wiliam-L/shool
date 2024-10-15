from rest_framework import serializers
from django.db import IntegrityError
from .models import Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'description', 'creation_date', 'update_date']

        extra_kwargs = {
            'name': {'required': True}
        }

    def validate(self, data):
        instance = self.instance
        name = data.get('name', instance.name if instance else None)
        description = data.get('description', instance.description if instance else None)

        if not instance:
            if name and Grade.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError(f'El grado: {name} ya existe.')

        else:
            if name and Grade.objects.filter(name__iexact=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError(f'{name} ya existe.')
            
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


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')
        return representation