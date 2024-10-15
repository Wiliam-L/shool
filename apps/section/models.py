from django.db import models

class Section(models.Model):
    name = models.CharField(max_length=1)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = "section"
    
    def __str__(self): return self.name