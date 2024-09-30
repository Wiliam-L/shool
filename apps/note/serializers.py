from rest_framework import serializers
from django.db import IntegrityError
from .models import Note
from apps.registration.models import CourseRegistration
from apps.course.models import Course
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

class NoteSerializers(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    section = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ['id', 'course', 'section', 'note', 'status_note', 'student', 'teacher', 'level', 'creation_date', 'update_date']
        
        extra_kwargs = {
            'course': {'required': True},
            'student': {'required': True},
            'teacher': {'required': True},
            'note': {'required': True}
        }
    
    def get_section(self, obj):
        try:
            registration = CourseRegistration.objects.get(course=obj.course, student=obj.student)
            return registration.section.name
        except CourseRegistration.DoesNotExist: return None 
    
    def get_level(self, obj):
        try:
            registration = CourseRegistration.objects.get(course=obj.course, student=obj.student)
            return registration.level.name
        except CourseRegistration.DoesNotExist: return None

    def __init__(self, *args, **kwargs):
        super(NoteSerializers, self).__init__(*args, **kwargs)

        if self.instance: 
            for field in ['course', 'student', 'teacher', 'note']:
                self.fields[field].required = False 
                self.fields[field].allow_blank = True

    def validate(self, data):
        student_id = data.get('student')
        course_id = data.get('course') 
        note = data.get('note')
        teacher_id = data.get('teacher')

        if not self.instance:  # Solo se ejecuta en la creación de una nueva nota
            if note == "":
                raise serializers.ValidationError({'error': 'La nota no puede ser vacía.'})

            # Verificar que el alumno está inscrito en algún curso en CourseRegistration
            registrations = CourseRegistration.objects.filter(student=student_id)

            if not registrations.exists():
                raise serializers.ValidationError({'error': 'El alumno no está asignado a ningún curso.'})

            # Verificar si el curso específico está en las inscripciones del estudiante
            if not registrations.filter(course__id=course_id.id).exists():
                raise serializers.ValidationError({'error': 'El alumno no está inscrito en este curso.'})

            # Verificar si el profesor está asignado al alumno en las inscripciones
            if not registrations.filter(teacher__id=teacher_id.id).exists():
                raise serializers.ValidationError({'error': 'El profesor no está asignado a este alumno.'})

            # Verificar si el profesor está asignado a este curso para el alumno
            if not registrations.filter(course__id=course_id.id, teacher__id=teacher_id.id).exists():
                raise serializers.ValidationError({'error': 'El profesor no está asignado a este curso para este alumno.'})

            # Validar que el curso y el profesor tienen la misma especialidad
            registration = registrations.filter(course__id=course_id.id).first()
            teacher_exists = registrations.filter(teacher__id=teacher_id.id).exists()

            if registration and teacher_exists:
                # Asegúrate de que estás usando los IDs correctos
                course_speciality = registration.course.filter(id=course_id.id).first().speciality
                teacher_speciality = Teacher.objects.filter(id=teacher_id.id).first()

                if teacher_speciality:
                    teacher_ = teacher_speciality.speciality.all()
                    if course_speciality not in teacher_:
                        raise serializers.ValidationError({
                            'error': 'El profesor no imparte este curso según su especialidad.'
                        })

            # Verificar si ya existe una nota para el mismo estudiante y curso
            if Note.objects.filter(student=student_id, course=course_id).exists():
                raise serializers.ValidationError({'error': 'Ya existe una nota para este alumno en este curso.'})

        else:
            registrations = CourseRegistration.objects.filter(student=self.instance.student)

            # Validar cuando se cambia `student`, `teacher`, y `course` al mismo tiempo
            if 'student' in data and 'teacher' in data and 'course' in data:
                registrations = CourseRegistration.objects.filter(student=student_id)
                
                # Verificar si el alumno está inscrito en el nuevo curso
                if not registrations.filter(course__id=course_id.id).exists():
                    raise serializers.ValidationError({'error': 'El alumno no está inscrito en este curso.'})

                # Verificar si el profesor está asignado al curso para este alumno
                if not registrations.filter(teacher__id=teacher_id.id, course__id=course_id.id).exists():
                    raise serializers.ValidationError({
                        'error': 'El profesor no está asignado a este curso para este alumno.'
                    })

                # Validar que la especialidad del profesor coincida con la del curso
                course_speciality = registrations.filter(course__id=course_id.id).first().course.speciality
                teacher_speciality = Teacher.objects.filter(id=teacher_id.id).first().speciality.all()

                if course_speciality not in teacher_speciality:
                    raise serializers.ValidationError({
                        'error': 'El profesor no tiene la especialidad requerida para este curso.'
                    })

            # Validar solo cuando se cambia el `teacher`
            elif 'teacher' in data and 'student' not in data and 'course' not in data:
                # Verificar si el nuevo profesor está asignado al estudiante en el curso actual
                if not registrations.filter(teacher__id=teacher_id.id, course__id=self.instance.course.id).exists():
                    raise serializers.ValidationError({
                        'error': 'El nuevo profesor no está asignado a este alumno para este curso.'
                    })

            # Validar solo cuando se cambia el `student`
            elif 'student' in data and 'teacher' not in data and 'course' not in data:
                # Verificar si el nuevo estudiante está inscrito en el curso actual con el profesor actual
                registrations = CourseRegistration.objects.filter(student=student_id)
                if not registrations.filter(course__id=self.instance.course.id, teacher__id=self.instance.teacher.id).exists():
                    raise serializers.ValidationError({
                        'error': 'El nuevo alumno no está inscrito en este curso con este profesor.'
                    })

            # Validar solo cuando se cambia el `course`
            elif 'course' in data and 'student' not in data and 'teacher' not in data:
                # Verificar si el nuevo curso está asignado al estudiante actual
                if not registrations.filter(course__id=course_id.id).exists():
                    raise serializers.ValidationError({
                        'error': 'El alumno no está inscrito en este curso.'
                    })

                # Validar que la especialidad del profesor coincida con la del nuevo curso
                course_speciality = Course.objects.filter(id=course_id.id).first().speciality
                teacher_speciality = Teacher.objects.filter(id=self.instance.teacher.id).first().speciality.all()

                if course_speciality not in teacher_speciality:
                    raise serializers.ValidationError({
                        'error': 'El profesor no tiene la especialidad requerida para este curso.'
                    })

            # Validar solo cuando se cambia la `nota`
            if 'note' in data:
                if note == "":
                    raise serializers.ValidationError({'error': 'La nota no puede ser vacía.'})

            
        return data


    def create(self, validated_data):
        try:
            note = Note.objects.create(**validated_data)
            note.save()
            return note
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})


    def to_representation(self, instance):
        representation =  super().to_representation(instance)

        if instance.course: representation['course'] = {instance.course.name}
        if instance.student: representation['student'] = {instance.student.name}
        if instance.teacher: representation['teacher'] = {instance.teacher.name}
        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según necesites

        return representation 
            