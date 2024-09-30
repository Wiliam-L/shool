from rest_framework import serializers
from .models import Student
from apps.tutor.models import Tutor
from apps.administrator.namesGroup import StudentNames
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from apps.registration.serializers import CourseRegistration, CourseRegistrationSerializer
from apps.course.serializers import CourseSerializer
from apps.teacher.serializers import TeacherSerializer
from apps.tutor.serializers import Tutor, TutorSerializer

class StudentForTeacher(serializers.ModelSerializer):
    tutor = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()

    class Meta:
        model=Student
        fields = ['name', 'suspended_student', 'tutor', 'courses', 'teachers']

    def get_tutor(self, obj):
        return {'name': obj.tutor.name}
    
    def get_courses(self, obj):
        registrations = CourseRegistration.objects.filter(student=obj)
        return CourseSerializer(registrations.values('course'), many=True).data

    def get_teachers(self, obj):
        registrations = CourseRegistration.objects.filter(student=obj)
        return TeacherSerializer(registrations.values('teacher'), many=True).data

class StudentShortSerializer(serializers.ModelSerializer):
    tutor = serializers.SerializerMethodField()
    class Meta: 
        model = Student 
        fields = ['id', 'name', 'suspended_student', 'email', 'phone', 'emergency_contact', 'address', 'tutor']

    def get_tutor(self, obj):
        if obj.tutor: 
            return {
                'name': obj.tutor.name
            }

class StudentAllSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True) 
    tutor = serializers.PrimaryKeyRelatedField(queryset=Tutor.objects.all(), required=True)

    class Meta:    
        model = Student
        fields = ["id", "name", "phone", "birthdate", 
                "address", "emergency_contact", "creation_date", "update_date",
                "suspended_student", "user", "tutor"
        ]

        extra_kwargs = {
            "name": {'required':True}, 
            "phone": {'required':True}, 
            "birthdate": {'required':True}, 
            "address": {'required':True}, 
            "emergency_contact": {'required':True},
            "user": {'required':True}, 
            "tutor": {'required':True}, 
        }
        
    def __init__(self, *args, **kwargs) -> None:
        super(StudentAllSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in  ["name", "phone", "birthdate", "address", "emergency_contact", "user", "tutor"]:
                self.fields[field].required = False
                self.fields[field].allow_blank = True

    def validate(self, data):
        instance = self.instance
        user = data.get('user')
        name = data.get('name')

        if not instance:

            try:
                groupname = user.groups.first().name if user.groups.exists() else None
            except Exception as e:
                raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})


            if name and Student.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError({"Error": "alumno existente"})

            if not groupname:
                raise serializers.ValidationError(f"El usuario no pertenece a ningún grupo.")

            NAMES_STUDENTS_SET = {name.lower() for name in StudentNames()}
            if groupname.lower() not in NAMES_STUDENTS_SET:
                raise serializers.ValidationError(f"El grupo no es correcto para este usuario: {user}. Se encontró: {groupname}")

            if Student.objects.filter(user=user).exists():
                raise serializers.ValidationError(f"El usuario ya está asignado a otro alumno.")

        else:
            
            if 'user' in data and instance.user != user:
                groupname = user.groups.first().name if user.groups.exists() else None

                if not groupname:
                    raise serializers.ValidationError(f"El usuario no pertenece a ningún grupo.")
                
                NAMES_STUDENTS_SET = {name.lower() for name in StudentNames()}
                if groupname.lower() not in NAMES_STUDENTS_SET:
                    raise serializers.ValidationError(f"El grupo no es correcto para este usuario: {user}. Se encontró: {groupname}")

            if name and Student.objects.filter(name__iexact=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"Error": "alumno existente"})

            if Student.objects.filter(user=user).exclude(id=instance.id).exists():
                raise serializers.ValidationError(f"El usuario ya está asignado a otro alumno.")

        return data
        
    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('userType', None)
        try:
            student = Student.objects.create(**validated_data)
            student.save()
            return student
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()
        return instance

    def to_representation(self, instance):
        respresentation = super().to_representation(instance)
        
        user = instance.user
        if user:
            respresentation['user'] = {
                'username': user.username,
                'email': user.email
            }

        tutor = instance.tutor
        if tutor:
            respresentation['tutor'] = {
                'tutor': tutor.name
            }

        respresentation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        respresentation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')


        return respresentation