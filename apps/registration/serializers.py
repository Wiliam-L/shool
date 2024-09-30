from rest_framework import serializers
from django.db import transaction, IntegrityError
from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from .models import CourseRegistration
from apps.course.models import Level, Course
from apps.section.models import Section
from apps.teacher.models import Teacher
from apps.student.models import Student

class ShortCourseRegistrationSerializer(serializers.ModelSerializer):
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    course = serializers.PrimaryKeyRelatedField(many=True, queryset=Course.objects.all())
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(many=True, queryset=Teacher.objects.all())
    tutor = serializers.SerializerMethodField()

    class Meta:
        model = CourseRegistration
        fields = ['student', 'course', 'level', 'section', 'teacher', 'tutor', 'start_time', 'end_time', 'create_date']
    

    def get_tutor(self, obj):
        if obj.student and obj.student.tutor:
            return {'name': obj.student.tutor.name, 'email': obj.student.tutor.email}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        courses = instance.course.all()
        if courses:
            representation['course'] = {course.name for course in courses}        
        
        teachers = instance.teacher.all()
        if teachers:
            representation['teacher'] = {teacher.name for teacher in teachers}        
        
        if instance.level: representation['level'] = {instance.level.name}
        if instance.section: representation['section'] = {instance.section.name}
        if instance.student: representation['student'] = {instance.student.name}
        
        representation['create_date'] = instance.create_date.strftime('%y-%m-%d %H:%M:%S')
        return representation

class CourseRegistrationSerializer(serializers.ModelSerializer):
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    course = serializers.PrimaryKeyRelatedField(many=True, queryset=Course.objects.all())
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(many=True, queryset=Teacher.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta: 
        model = CourseRegistration
        fields = ['id', 'student', 'level', 'course', 'section', 'teacher', 'start_time', 'end_time', 'create_date', 'update_date']

        extra_kwargs = {
            'level': {'required': True},
            'course': {'required': True},
            'section': {'required': True},
            'teacher': {'required': True},
            'start_time': {'required': True},
            'end_time': {'required': True},
            'student': {'required': True}
        }
    
    def __init__(self, *args, **kwargs):
        super(CourseRegistrationSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in ['level', 'course', 'section', 'teacher', 'start_time', 'end_time', 'student']:
                self.fields[field].required = False
                self.fields[field].allow_blank = True

    def validate(self, data):
        instance = self.instance
        level = data.get('level')
        student = data.get('student')
        teachers = data.get('teacher', [])
        courses = data.get('course', [])
        start_time = data.get('start_time')
        end_time = data.get('end_time')
            
        try:    
            if not instance:
                    self._validateStudentAsignment(student=student)
                    teacher_ids = self._getTeachersIds(teachers=teachers)
                    course_ids = self._getCoursesIds(courses=courses)
                    teachers_info = self._getTeachersInfo(teacher_ids=teacher_ids)
                    teacher_speciality_map = self._getTeacherSpeciality(teachers_info=teachers_info)                      
                    teacher_level_map = self._getTeacherLevel(teachers_info=teachers_info)
                    courses_info = self._getCourseSpeciality(course_ids=course_ids)

                    self._validateSpeciality(courses_info=courses_info, teacher_ids=teacher_ids, teacher_speciality_map=teacher_speciality_map)
                    self._validateLevelInTeacher(teacher_level_map=teacher_level_map, level=level, teacher_ids=teacher_ids)

                    if CourseRegistration.objects.filter(
                            teacher__in=teacher_ids,
                            start_time__lt=end_time,
                            end_time__gt=start_time,                             
                        ).exists():
                        raise serializers.ValidationError({
                            'error': 'Conflicto de horario: El profesor ya tiene otro curso en el mismo horario.'
                        })
                    
                    # Validar que el nivel proporcionado coincida con el nivel del profesor
                    for teacher_id in teacher_ids:
                        if level.id != teacher_level_map[teacher_id]:
                            raise serializers.ValidationError({
                                'error': f'El nivel asignado no coincide con el nivel del profesor con ID {teacher_id}.'
                            })
            else:   
                    if not level: level = instance.level
                    if not teachers: teachers = instance.teacher.all()
                    if not courses: courses = instance.course.all()

                    if teachers and courses and level:
                        teacher_ids = self._getTeachersIds(teachers=teachers)
                        course_ids = self._getCoursesIds(courses=courses)
                        teachers_info = self._getTeachersInfo(teacher_ids=teacher_ids)
                        teacher_speciality_map = self._getTeacherSpeciality(teachers_info=teachers_info)                      
                        teacher_level_map = self._getTeacherLevel(teachers_info=teachers_info)
                        courses_info = self._getCourseSpeciality(course_ids=course_ids)

                        self._validateSpeciality(courses_info=courses_info, teacher_ids=teacher_ids, teacher_speciality_map=teacher_speciality_map)
                        self._validateLevelInTeacher(teacher_level_map=teacher_level_map, level=level, teacher_ids=teacher_ids)
                        self._validateLevel(level=level)

                        # Validar que no haya conflictos de horario
                        start_time = data.get('start_time', instance.start_time)
                        end_time = data.get('end_time', instance.end_time)

                        if CourseRegistration.objects.filter(
                                teacher__in=teacher_ids,
                                start_time__lt=end_time,
                                end_time__gt=start_time
                            ).exclude(id=instance.id).exists():
                            raise serializers.ValidationError({
                                'error': 'Conflicto de horario: El profesor ya tiene otro curso en el mismo horario.'
                            })
                        
                    elif teachers:
                        #Cuando solo se cambia el profesor
                        teacher_ids = self._getTeachersIds(teachers=teachers)
                        teachers_info = self._getTeachersInfo(teacher_ids=teacher_ids)
                        teacher_speciality_map = self._getTeacherSpeciality(teachers_info=teachers_info)                      
                        
                        if level:
                            teacher_level_map = self._getTeacherLevel(teachers_info=teachers_info)
                            self._validateLevelInTeacher(teacher_level_map=teacher_level_map, level=level, teacher_ids=teacher_ids)
                    
                    elif courses:
                        #Cuando solo se cambia el curso
                        course_ids = self._getCoursesIds(courses=courses)
                        courses_info = self._getCourseSpeciality(course_ids=course_ids)
                        course_speciality = {course.id: course_speciality for course in courses_info}

                        if teachers:
                            teacher_ids = self._getTeachersIds(teachers=teachers)
                            teachers_info = self._getTeachersInfo(teacher_ids=teacher_ids)
                            teacher_speciality_map = self._getTeacherSpeciality(teachers_info=teachers_info)
                            teacher_level_map = self._getTeacherLevel(teachers_info=teachers_info)

                            self._validateSpeciality(courses_info=courses_info, teacher_ids=teacher_ids, teacher_speciality_map=teacher_speciality_map)
                            self._validateLevelInTeacher(teacher_level_map=teacher_level_map, level=level, teacher_ids=teacher_ids)

                    elif level:
                        #cuando solo se cambia de nivel
                        self._validateLevel(level=level)    


        except ObjectDoesNotExist as e:
            raise serializers.ValidationError({'error': 'Error: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})

        return data

    def _getTeachersIds(self, teachers):
        return [teacher.id for teacher in teachers] if isinstance(teachers, (list, QuerySet)) else [teachers.id]
    
    def _getCoursesIds(self, courses):
        return  [course.id for course in courses] if isinstance(courses, (list, QuerySet)) else [courses.id]

    def _getTeachersInfo(self, teacher_ids,):
        teachers_info = Teacher.objects.filter(id__in=teacher_ids).values_list('id', 'speciality', 'level', flat=False)
        return teachers_info
    
    def _getTeacherSpeciality(self, teachers_info):
        teacher_speciality_map = {info[0]: info[1] for info in teachers_info}
        return teacher_speciality_map
    
    def _getTeacherLevel(self, teachers_info):
        teacher_level_map = {info[0]: info[2] for info in teachers_info}
        return teacher_level_map
                       
    def _getCourseSpeciality(self, course_ids):
        courses_info = Course.objects.filter(id__in=course_ids).values_list('id', 'speciality', flat=False)
        return courses_info
    
    def _validateSpeciality(self, courses_info, teacher_ids, teacher_speciality_map):
        for course_id, course_speciality in courses_info:
            course_has_teacher = False
            for teacher_id in teacher_ids:
                if teacher_speciality_map[teacher_id] == course_speciality:
                    course_has_teacher = True
                    break

            if not course_has_teacher:
                raise serializers.ValidationError({
                    'error': f'El curso con ID {course_id} requiere un profesor con la especialidad {course_speciality}, pero no hay ningún profesor asignado con esa especialidad.'
                })

    def _validateLevelInTeacher(self, teacher_ids, level, teacher_level_map):
        for teacher_id in teacher_ids:
            if level.id != teacher_level_map[teacher_id]:
                raise serializers.ValidationError({
                    'error': f'El nivel asignado no coincide con el nivel del profesor con ID {teacher_id}.'
                })
    
    def _validateLevel(self, level):
        if level and not Teacher.objects.filter(level=level.id):
            raise serializers.ValidationError({'error': f'El nivel no es adecuado, Profesor no es apto para este nivel: {level}.'})

    def _validateStudentAsignment(self, student):
        if CourseRegistration.objects.filter(student=student).exists():
            raise serializers.ValidationError({'error': 'El estudiante ya tiene una asignación, no se puede crear otra asignación.'})

    @transaction.atomic
    def create(self, validated_data):
        try:
            courses = validated_data.pop('course', [])
            teachers = validated_data.pop('teacher', [])

            course_registration = CourseRegistration.objects.create(**validated_data)
            course_registration.course.set(courses)
            course_registration.teacher.set(teachers)
            
            course_registration.save()
            return course_registration    
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.student: representation['student'] = {instance.student.name}
        if instance.course: representation['course'] = {instance.course.name}
        if instance.level: representation['level'] = {instance.level.name}
        if instance.section: representation['section'] = {instance.section.name}

        teachers = instance.teacher.all()
        if teachers:
            representation['teacher'] = {teacher.name for teacher in teachers}

        courses = instance.course.all()
        if courses:
            representation['course'] = {course.name for course in courses}

        representation['create_date'] = instance.create_date.strftime('%Y-%m-%d %H:%M:%S')
        representation['update_date'] = instance.update_date.strftime('%Y-%m-%d %H:%M:%S')
        return representation