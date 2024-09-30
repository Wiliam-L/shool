from rest_framework import serializers
from django.db import transaction
from .models import Course, Level
from apps.teacher.models import Speciality

class CourseSerializer(serializers.ModelSerializer):
    speciality = serializers.PrimaryKeyRelatedField(queryset=Speciality.objects.all())

    class Meta:
        model = Course
        fields = ['id', 'name', 'speciality', 'description', 'creation_date', 'update_date']

        extra_kwargs = {
            'name': {'required': True},
            'speciality': {'required': True}
        }

     
    def __init__(self, *args, **kwargs):
        super(CourseSerializer, self).__init__(*args, **kwargs)
        
        if self.instance:
            for field in ['name', 'speciality']:
                self.fields[field].required = False
                self.fields[field].allow_blank = True


    def validate(self, data):
        name = data.get('name')
        instance = self.instance 
        
        if instance:
            # Verifica si el nombre ya existe
            if name and Course.objects.filter(name__iexact=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError({'error': f'el curso {name} ya existe'})
        else:
            if name and Course.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError({'error': f"curso: {name} ya existe."})
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.speciality: 
            representation['speciality'] = {instance.speciality.name}
        
        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')

        return representation

class ShortLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['name']
  
class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'creation_date', 'update_date']

    def validate(self, data):
        name = data.get('name')
        if name and Level.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError({'error': f'el nivel {name} ya existe'})
        
        return data


    @transaction.atomic
    def create(self, validated_data):
        return super().create(validated_data)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites
        return representation