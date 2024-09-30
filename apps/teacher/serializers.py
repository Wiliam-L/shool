from rest_framework import serializers
from .models import Speciality, Teacher
from apps.course.models import Level
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from apps.administrator.namesGroup import TeacherNames
from apps.section.serializers import Section, SectionSerializer
from apps.registration.serializers import CourseRegistration, CourseRegistrationSerializer, Course
from apps.course.serializers import ShortLevelSerializer

class SpecialitySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Speciality
        fields = ['id', 'name']

    def create(self, validated_data):
        speciality = Speciality.objects.create(
            name = validated_data['name']
        )
        return speciality

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
        }
        

class ShortTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['name', 'speciality', 'level']
    

class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    level = serializers.PrimaryKeyRelatedField(many=True, queryset=Level.objects.all(), required=False)
    speciality = serializers.PrimaryKeyRelatedField(many=True, queryset=Speciality.objects.all(), required=False)
    
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'phone', 'speciality', 'user', 'level', 'create_date', 'update_date']

        extra_kwargs = {
            'name': {'required': True},
            'phone': {'required': True},
            'speciality': {'required': True},
            'user': {'required': True},
            'level': {'required': True}
        }

    def __init__(self, *args, **kwargs):
        super(TeacherSerializer, self).__init__(*args, **kwargs)
        
        if self.instance:
            for field in ['name', 'phone', 'speciality', 'user', 'level']:
                self.fields[field].required = False 
                self.fields[field].allow_blank = True

    def validate(self, data):
        instance = self.instance
        name = data.get('name')
        speciality = data.get('speciality')
        user = data.get('user')
        level = data.get('level')

        if not instance:
            try:
                groupname = user.groups.first().name if user.groups.exists() else None
            except Exception as e:
                raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})

            if name and Teacher.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError({"Error": f"profesor {name} ya existente"})

            if not groupname:
                raise serializers.ValidationError(f"El usuario no pertenece a ningún grupo.")

            if groupname.lower() not in {namest.lower() for namest in TeacherNames()}:
                raise serializers.ValidationError(f"El grupo no es correcto para este usuario. Se encontró: {groupname}")
            
            # Validar existencia de niveles y especialidades
            for lvl in level:
                if not Level.objects.filter(id=lvl.id).exists():
                    raise serializers.ValidationError(f"El nivel con ID {lvl.id} no existe.")

            for spec in speciality:
                if not Speciality.objects.filter(id=spec.id).exists():
                    raise serializers.ValidationError(f"La especialidad con ID {spec.id} no existe.")
            
            if Teacher.objects.filter(user=user).exists():
                raise serializers.ValidationError(f"El usuario ya está asignado a otro tutor.")

        else: pass

        return data
    
    @transaction.atomic
    def create(self, validated_data):
        try:
            specialities = validated_data.pop('speciality', [])
            levels = validated_data.pop('level', [])
            teacher = Teacher.objects.create(**validated_data)
            teacher.speciality.set(specialities)
            teacher.level.set(levels)
            
            teacher.save()

            return teacher
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        specialities = instance.speciality.all()
        if specialities:
            representation['speciality'] = {speciality.name for speciality in specialities}
        
        levels = instance.level.all()
        if levels: representation['level'] = {level.name for level in levels}
        
        if instance.user: representation['user'] = {instance.user.email}
        representation['create_date'] = instance.create_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites

        return representation  

class CourseWithSectionSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()  
    end_time = serializers.SerializerMethodField()    
    
    class Meta:
        model = Course
        fields = ['name', 'speciality', 'sections', 'level', 'start_time', 'end_time', 'creation_date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.speciality:
            representation['speciality'] = {
                'name': instance.speciality.name
            }

        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        return representation
    
    def get_level(self, obj):
        registrations = CourseRegistration.objects.filter(course=obj)
        levels = Level.objects.filter(courseregistration__in=registrations).distinct()
        return ShortLevelSerializer(levels, many=True).data

    def get_sections(self, obj):
        registrations = CourseRegistration.objects.filter(course=obj)
        return [{'name': registration.section.name} for registration in registrations]

    def get_start_time(self, obj):
        registrations = CourseRegistration.objects.filter(course=obj).first()
        return registrations.start_time if registrations else None

    def get_end_time(self, obj):
        registrations = CourseRegistration.objects.filter(course=obj).first()
        return registrations.end_time if registrations else None
