from django.test import TestCase
from django.contrib.auth.models import User
from apps.teacher.models import Teacher
from apps.grade.models import Grade
from apps.section.models import Section
from apps.course.models import Course, Speciality, CourseSchedule, TeacherCourseAssignment
from rest_framework.exceptions import ValidationError
from datetime import time
from .serializers import TeacherCourseAssignmentSerializer

class TeacherCourseAssignmentSerializerTestCase(TestCase):
    def setUp(self):
        # Crear usuario y profesor
        self.user_juan = User.objects.create(username='juan', email='juan@ejemplo.com')
        self.profesor_juan = Teacher.objects.create(user=self.user_juan, name='Profesor Juan')

        # Asignar especialidad
        self.especialidad_matematicas = Speciality.objects.create(name='Matemáticas')
        self.profesor_juan.speciality.add(self.especialidad_matematicas)

        # Crear grado, sección y curso
        self.grado_1 = Grade.objects.create(name='1° básico')
        self.seccion_a = Section.objects.create(name='A')
        self.curso_matematicas = Course.objects.create(name='Matemáticas', speciality=self.especialidad_matematicas)

        # Crear horarios
        self.horario_7_9 = CourseSchedule.objects.create(start_time=time(7, 0), end_time=time(9, 0))
        self.horario_11_12 = CourseSchedule.objects.create(start_time=time(11, 0), end_time=time(12, 0))

    def test_crear_asignacion_valida(self):
        data = {
            'teacher': self.profesor_juan.id,
            'course': self.curso_matematicas.id,
            'grade': self.grado_1.id,
            'section': self.seccion_a.id,
            'schedule': self.horario_7_9.id
        }
        serializer = TeacherCourseAssignmentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        assignment = serializer.save()
        self.assertEqual(assignment.teacher, self.profesor_juan)
        self.assertEqual(assignment.course, self.curso_matematicas)
        self.assertEqual(assignment.grade, self.grado_1)
        self.assertEqual(assignment.section, self.seccion_a)
        self.assertEqual(assignment.schedule, self.horario_7_9)

    def test_crear_asignacion_profesor_no_especializado(self):
        # Crear otro curso con diferente especialidad
        especialidad_historia = Speciality.objects.create(name='Historia')
        curso_historia = Course.objects.create(name='Historia', speciality=especialidad_historia)
        
        data = {
            'teacher': self.profesor_juan.id,
            'course': curso_historia.id,
            'grade': self.grado_1.id,
            'section': self.seccion_a.id,
            'schedule': self.horario_11_12.id
        }
        serializer = TeacherCourseAssignmentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('teacher', serializer.errors)
        self.assertEqual(
            serializer.errors['teacher'][0],
            f"El profesor {self.profesor_juan.name} no está especializado en {curso_historia.speciality.name}."
        )

    def test_crear_asignacion_con_traslape_de_horario(self):
        # Crear una asignación inicial
        TeacherCourseAssignment.objects.create(
            teacher=self.profesor_juan,
            course=self.curso_matematicas,
            grade=self.grado_1,
            section=self.seccion_a,
            schedule=self.horario_7_9
        )

        # Intentar crear otra asignación con el mismo horario, grado y sección
        data = {
            'teacher': self.profesor_juan.id,
            'course': self.curso_matematicas.id,
            'grade': self.grado_1.id,
            'section': self.seccion_a.id,
            'schedule': self.horario_7_9.id
        }
        serializer = TeacherCourseAssignmentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('schedule', serializer.errors)
        self.assertEqual(
            serializer.errors['schedule'][0],
            f"El profesor {self.profesor_juan.name} ya tiene una asignación en el horario {self.horario_7_9} para {self.grado_1} {self.seccion_a}."
        )

    def test_actualizar_asignacion_cambiar_profesor_valido(self):
        # Crear una asignación inicial
        assignment = TeacherCourseAssignment.objects.create(
            teacher=self.profesor_juan,
            course=self.curso_matematicas,
            grade=self.grado_1,
            section=self.seccion_a,
            schedule=self.horario_7_9
        )

        # Crear otro profesor con la misma especialidad
        user_maria = User.objects.create(username='maria', email='maria@ejemplo.com')
        profesor_maria = Teacher.objects.create(user=user_maria, name='Profesora María')
        profesor_maria.speciality.add(self.especialidad_matematicas)

        data = {
            'teacher': profesor_maria.id,
            'schedule': self.horario_11_12.id
        }

        serializer = TeacherCourseAssignmentSerializer(instance=assignment, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_assignment = serializer.save()
        self.assertEqual(updated_assignment.teacher, profesor_maria)
        self.assertEqual(updated_assignment.schedule, self.horario_11_12)

    def test_actualizar_asignacion_cambiar_profesor_no_especializado(self):
        # Crear una asignación inicial
        assignment = TeacherCourseAssignment.objects.create(
            teacher=self.profesor_juan,
            course=self.curso_matematicas,
            grade=self.grado_1,
            section=self.seccion_a,
            schedule=self.horario_7_9
        )

        # Crear otro profesor sin la especialidad requerida
        especialidad_historia = Speciality.objects.create(name='Historia')
        user_pedro = User.objects.create(username='pedro', email='pedro@ejemplo.com')
        profesor_pedro = Teacher.objects.create(user=user_pedro, name='Profesor Pedro')
        profesor_pedro.speciality.add(especialidad_historia)

        data = {
            'teacher': profesor_pedro.id
        }

        serializer = TeacherCourseAssignmentSerializer(instance=assignment, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('teacher', serializer.errors)
        self.assertEqual(
            serializer.errors['teacher'][0],
            f"El profesor {profesor_pedro.name} no está especializado en {self.curso_matematicas.speciality.name}."
        )

    def test_actualizar_asignacion_completamente_con_put(self):
        # Crear una asignación inicial
        assignment = TeacherCourseAssignment.objects.create(
            teacher=self.profesor_juan,
            course=self.curso_matematicas,
            grade=self.grado_1,
            section=self.seccion_a,
            schedule=self.horario_7_9
        )

        # Crear otro profesor con la especialidad necesaria
        user_maria = User.objects.create(username='maria', email='maria@ejemplo.com')
        profesor_maria = Teacher.objects.create(user=user_maria, name='Profesora María')
        profesor_maria.speciality.add(self.especialidad_matematicas)

        # Datos completos para PUT
        data = {
            'teacher': profesor_maria.id,
            'course': self.curso_matematicas.id,
            'grade': self.grado_1.id,
            'section': self.seccion_a.id,
            'schedule': self.horario_11_12.id
        }

        serializer = TeacherCourseAssignmentSerializer(instance=assignment, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_assignment = serializer.save()
        self.assertEqual(updated_assignment.teacher, profesor_maria)
        self.assertEqual(updated_assignment.schedule, self.horario_11_12)
