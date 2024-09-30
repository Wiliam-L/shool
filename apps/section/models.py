from django.db import models
from apps.course.models import Level

class Section(models.Model):
    name = models.CharField(max_length=1)
    description = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.PROTECT) 
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = "section"
    
    def __str__(self): return self.name