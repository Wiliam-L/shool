from rest_framework import serializers
from django.db import IntegrityError, transaction
from .models import Note
from apps.registration.models import CourseRegistration
from apps.course.models import Course, TeacherCourseAssignment
from apps.student.models import Student
from apps.teacher.models import Teacher

class ShortNoteSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    
    class Meta:
        model = Note
        fields = ['student', 'course', 'note', 'status_note', 'teacher', 'creation_date']

    def to_representation(self, instance):
        representation =  super().to_representation(instance)

        if instance.course:
            representation['course'] = {instance.course.name}
                    
        if instance.teacher:
            representation['teacher'] = {instance.teacher.name}
        if instance.student: 
            representation['student'] = {instance.student.name}

        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        return representation

#serializador para notas del estudiante
class NoteSerializers(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    grade = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ['id', 'course', 'note', 'status_note', 'student', 'teacher', 'grade', 'section', 'creation_date', 'update_date']
        
        extra_kwargs = {
            'course': {'required': True},
            'student': {'required': True},
            'teacher': {'required': True},
            'note': {'required': True}
        }

    def get_grade(self, obj):
        teacher_course_assignment = TeacherCourseAssignment.objects.filter(teacher=obj.teacher, course=obj.course).first()
        if teacher_course_assignment:
            return teacher_course_assignment.grade.name
        return None
    
    def get_section(self, obj):
        teacher_course_assignment = TeacherCourseAssignment.objects.filter(teacher=obj.teacher, course=obj.course).first()
        if teacher_course_assignment:
            return teacher_course_assignment.section.name  
        return None

    def validate(self, data):
        instance = self.instance
        course = data.get('course', instance.course if instance else None)
        note = data.get('note', instance.note if instance else None)
        status = data.get('status_note', instance.status_note if instance else None)
        student = data.get('student', instance.student if instance else None)
        teacher = data.get('teacher', instance.teacher if instance else None)

         # Validar que al menos uno de los campos esté presente (si alguno se actualizó)
        if not course or not student or not teacher:
            raise serializers.ValidationError('Debe proporcionar un curso, estudiante y profesor válidos para la validación.')

        # Verificar que la combinación de estudiante, curso y profesor es válida
        course_registration = CourseRegistration.objects.filter(
            student=student, 
            teacher_course_assignment__course=course, 
            teacher_course_assignment__teacher=teacher
        )

        if not course_registration.exists():
            raise serializers.ValidationError({
                'course': 'El estudiante no está asignado a este curso con este profesor.'
            })

        return data
        

    @transaction.atomic
    def create(self, validated_data):
        try:
            note = Note.objects.create(**validated_data)
            note.save()
            return note
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})

    def to_representation(self, instance):
        representation =  super().to_representation(instance)

        if instance.course: representation['course'] = {instance.course.name}
        if instance.student: representation['student'] = {instance.student.name}
        if instance.teacher: representation['teacher'] = {instance.teacher.name}
        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')
        return representation 
            