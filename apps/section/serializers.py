from rest_framework import serializers
from django.db import IntegrityError, transaction
from .models import Section

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name', 'description']

        extra_kwargs = {
            'name': {'required': True}
        }


    def validate(self, data):
        name = data.get('name')
        if name and Section.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError({'name': f'la seccion {name} ya existe'})
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        try:
            section = Section.objects.create(**validated_data)
            return section
        
        except IntegrityError as e:
            raise serializers.ValidationError({'error': 'Error de integridad: ' + str(e)})    
        except ValueError: 
            raise serializers.ValidationError({'error': 'Error de valor: ' + str(e)})
        except Exception as e:
            raise serializers.ValidationError({'error': 'Error inesperado: ' + str(e)})
        