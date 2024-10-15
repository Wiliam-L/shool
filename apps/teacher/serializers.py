from rest_framework import serializers
from .models import Speciality, Teacher
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from apps.administrator.namesGroup import TeacherNames
from apps.registration.serializers import CourseRegistration, TeacherCourseAssignment

#serializador para especialidad
class SpecialitySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Speciality
        fields = ['id', 'name']

    @transaction.atomic
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
        fields = ['name', 'speciality']

#información del profesor sobre sus cursos por grado
class TeacherCourseAssignmentSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.name')
    grade = serializers.CharField(source='grade.name')
    section = serializers.CharField(source='section.name')
    teacher_name = serializers.CharField(source='teacher.name')  

    class Meta:
        model = TeacherCourseAssignment
        fields = ['course', 'grade', 'section', 'teacher_name']  

#información completa para profesor de asignación
class TeacherForAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    speciality = serializers.PrimaryKeyRelatedField(many=True, queryset=Speciality.objects.all(), required=True)
    course_assignments = TeacherCourseAssignmentSerializer(source='teachercourseassignment_set', many=True, read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'phone', 'speciality', 'user', 'course_assignments', 'create_date', 'update_date']

#serializador de profesor para tutor
class TeacherForTutorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    speciality = serializers.PrimaryKeyRelatedField(many=True, queryset=Speciality.objects.all())
    grade = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'name', 'phone', 'speciality', 'user', 'grade', 'section', 'create_date', 'update_date']

    def get_grade(self, obj):
        teacher_assignmet = TeacherCourseAssignment.objects.filter(teacher=obj).first()
        if teacher_assignmet:
            return teacher_assignmet.grade.name
        return None
    
    def get_section(self, obj):
        teacher_assignment = TeacherCourseAssignment.objects.filter(teacher=obj).first()
        if teacher_assignment:
            return teacher_assignment.section.name
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        specialities = instance.speciality.all()
        if specialities:
            representation['speciality'] = {speciality.name for speciality in specialities}
        
        if instance.user: representation['user'] = {'email': instance.user.email}
        return representation
    
#serializador para profesor
class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    speciality = serializers.PrimaryKeyRelatedField(many=True, queryset=Speciality.objects.all())

    class Meta:
        model = Teacher
        fields = ['id', 'name', 'phone', 'speciality', 'user', 'create_date', 'update_date']

        extra_kwargs = {
            'name': {'required': True},
            'phone': {'required': True},
            'speciality': {'required': True},
            'user': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        super(TeacherSerializer, self).__init__(*args, **kwargs)
        
        if self.instance:
            for field in ['name', 'phone', 'speciality', 'user']:
                self.fields[field].required = False 
                self.fields[field].allow_blank = True

    def validate(self, data):
        instance = self.instance
        name = data.get('name')
        speciality = data.get('speciality')
        user = data.get('user')

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
            teacher = Teacher.objects.create(**validated_data)
            teacher.speciality.set(specialities)
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
        
        if instance.user: representation['user'] = {instance.user.email}
        representation['create_date'] = instance.create_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites

        return representation  

#curso asignados al profesor
class TeacherCourseAssignmentSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()  
    grade = serializers.StringRelatedField()
    section = serializers.StringRelatedField()
    teacher = serializers.CharField(source='teacher.name')
    schedule = serializers.StringRelatedField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = TeacherCourseAssignment
        fields = ['teacher', 'student', 'course', 'grade', 'section', 'schedule'] 

    def get_student(self, obj):
        registrations = CourseRegistration.objects.filter(teacher_course_assignment=obj)
        students = registrations.values_list('student__name', flat=True).distinct() 
        return list(students)