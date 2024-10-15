from django.db import models

class Grade(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'grade'
    
    def __str__(self): return self.name