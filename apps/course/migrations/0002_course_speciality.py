# Generated by Django 5.1.1 on 2024-09-25 06:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
        ('teacher', '0002_remove_teacher_level_alter_teacher_speciality_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='speciality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='teacher.speciality'),
        ),
    ]
