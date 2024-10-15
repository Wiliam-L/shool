from rest_framework import serializers
from django.db import transaction, IntegrityError
from .models import CourseRegistration, Grade, Section
from apps.course.models import TeacherCourseAssignment
from apps.section.models import Section
from apps.student.models import Student

class CourseRegistrationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), required=True)
    teacher_course_assignment = serializers.PrimaryKeyRelatedField(queryset=TeacherCourseAssignment.objects.all(), many=True, required=True)
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), required=True)
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all(), required=True)

    class Meta: 
        model = CourseRegistration
        fields = ['id', 'student', 'section', 'grade', 'teacher_course_assignment', 'create_date', 'update_date']

    def validate(self, data):
        instance = self.instance
        student = data.get('student', instance.student if instance else None )
        teachers = data.get('teacher_course_assignment', instance.teacher_course_assignment.all() if instance else None)
        grade = data.get('grade', instance.grade if instance else None)
        section = data.get('section', instance.section if instance else None)

        if student:
            student_state = Student.objects.filter(id=student.id).first()
            if student_state and student_state.suspended_student:
                raise serializers.ValidationError("Alumno inactivo, no se puede asignar cursos a alumnos inactivos.")
        
        # Validar los profesores
        if teachers:
            for teacher_assignment_id in teachers: 
                teacher_assignment = TeacherCourseAssignment.objects.filter(id=teacher_assignment_id.id).first()
            
                if not teacher_assignment:
                   raise serializers.ValidationError(f"El profesor con ID {teacher_assignment_id} no existe.")
                if teacher_assignment.grade != grade or teacher_assignment.section != section:
                    raise serializers.ValidationError(
                        f"El profesor {teacher_assignment.teacher.name} no está asignado a este grado o sección."
                    )

                available_assignments = TeacherCourseAssignment.objects.filter(grade=grade, section=section)
                if not available_assignments.exists():
                    raise serializers.ValidationError("No hay asignaciones de curso disponibles para el nuevo grado o sección.")

        return data

    @transaction.atomic
    def create(self, validated_data):
        try:
            teachers = validated_data.pop('teacher_course_assignment', [])
            course_registration = CourseRegistration.objects.create(**validated_data)
            course_registration.teacher_course_assignment.set(teachers)  # Asignar todos los profesores

            
            return course_registration  
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError as e: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})
        
    def to_representation(self, instance):
        representation =  super().to_representation(instance)

        if instance.student: representation['student'] = {'name': instance.student.name}
        if instance.section: representation['section'] = {'name': instance.section.name}
        if instance.grade: representation['grade'] = {'name': instance.grade.name}
        if instance.teacher_course_assignment.exists():
            assignments = []
            for assignment in instance.teacher_course_assignment.all():
                assignments.append({
                    'teacher': assignment.teacher.name,  # Asegúrate de que el modelo Teacher tenga un campo 'name'
                    'course': assignment.course.name,    # Asegúrate de que el modelo Course tenga un campo 'name'
                    'schedule': {
                        'start_time': assignment.schedule.start_time.strftime("%H:%M"),  # Formateo de hora
                        'end_time': assignment.schedule.end_time.strftime("%H:%M")      # Formateo de hora
                    }
                })
            representation['teacher_course_assignments'] = assignments
        
        if 'teacher_course_assignment' in representation:
            del representation['teacher_course_assignment']
    
        return representation