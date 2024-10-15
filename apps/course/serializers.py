from rest_framework import serializers
from django.db import transaction, IntegrityError
from .models import Course, CourseSchedule, TeacherCourseAssignment, Grade
from apps.teacher.models import Speciality, Teacher
from apps.registration.models import CourseRegistration

class CourseofStudent(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()  
    course = serializers.SerializerMethodField()   
    grade = serializers.SerializerMethodField()    
    schedule = serializers.SerializerMethodField() 
    section = serializers.SerializerMethodField()  
    student = serializers.SerializerMethodField() 

    class Meta:
        model = CourseRegistration  
        fields = ['id', 'course', 'student','teacher', 'grade', 'schedule', 'section']

    def get_student(self, obj):
        return obj.student.name if obj.student else None

    # Método para obtener el curso desde teacher_course_assignment
    def get_course(self, obj):
        teacher_course_assignment = obj.teacher_course_assignment.first()
        if teacher_course_assignment:
            return teacher_course_assignment.course.name
        return None

    # Método para obtener el profesor
    def get_teacher(self, obj):
        teacher_course_assignment = obj.teacher_course_assignment.first()
        if teacher_course_assignment:
            return teacher_course_assignment.teacher.name
        return None

    # Método para obtener el grado
    def get_grade(self, obj):
        return obj.grade.name if obj.grade else None


    # Método para obtener la sección
    def get_section(self, obj):
        return obj.section.name if obj.section else None


    # Método para obtener el horario desde teacher_course_assignment
    def get_schedule(self, obj):
        teacher_course_assignment = obj.teacher_course_assignment.first()
        if teacher_course_assignment:
            return str(teacher_course_assignment.schedule)
        return None


class CourseSerializer(serializers.ModelSerializer):
    speciality = serializers.PrimaryKeyRelatedField(queryset=Speciality.objects.all(), required=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'speciality', 'description', 'creation_date', 'update_date']

        extra_kwargs = {
            'name': {'required': True},
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


class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = '__all__'

class TeacherCourseAssignmentSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), required=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=True)
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), required=True)
    schedule = serializers.PrimaryKeyRelatedField(queryset=CourseSchedule.objects.all(), required=True)

    class Meta:
        model = TeacherCourseAssignment
        fields = ['id', 'teacher', 'course', 'grade', 'section', 'schedule', 'create_time', 'update_time']
        read_only_fields = ['id', 'create_time', 'update_time']
    
    def validate(self, data):
            instance = self.instance  # Puede ser None si es una creación
            teacher = data.get('teacher', instance.teacher if instance else None)
            course = data.get('course', instance.course if instance else None)
            schedule = data.get('schedule', instance.schedule if instance else None)
            grade = data.get('grade', instance.grade if instance else None)
            section = data.get('section', instance.section if instance else None)

            # Validar que el profesor tenga la especialidad requerida para el curso
            if teacher and course:
                if not teacher.speciality.filter(id=course.speciality.id).exists():
                    raise serializers.ValidationError(
                        f"El profesor {teacher.name} no está especializado en {course.speciality.name}."
                    )

            # Validar traslape de horarios
            if teacher and schedule and grade and section:
                overlapping_assignment = TeacherCourseAssignment.objects.filter(
                    teacher=teacher,
                    schedule=schedule,
                    grade=grade,
                    section=section
                ).exclude(id=instance.id if instance else None)

                if overlapping_assignment.exists():
                    raise serializers.ValidationError(
                        f"El profesor {teacher.name} ya tiene una asignación en el horario {schedule} para {grade} {section}."
                    )

            return data
    
    @transaction.atomic
    def create(self, validated_data):
        try:
            assignment = TeacherCourseAssignment.objects.create(**validated_data)
            return assignment
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        
    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        representation =  super().to_representation(instance)

        if instance.teacher: representation['teacher'] = {instance.teacher.name}
        if instance.course: representation['course'] = {instance.course.name}
        if instance.grade: representation['grade'] = {instance.grade.name}
        if instance.section: representation['section'] = {instance.section.name}
        if  instance.schedule: representation['schedule'] = {
            'start_time': instance.schedule.start_time.strftime('%H:%M'),
            'end_time': instance.schedule.end_time.strftime('%H:%M')
        }

        representation['create_time'] = instance.create_time.strftime('%Y-%m-%d %H:%M:%S')
        representation['update_time'] = instance.update_time.strftime('%Y-%m-%d %H:%M:%S')

        return representation