from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
from datetime import timedelta

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid.uuid4)
    creation_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    verificated = models.BooleanField(default=False)  # Asegúrate de tener este campo


    class Meta:
        db_table = 'email_verification'

    def __str__(self):
        return f'{self.user.email} - {self.code}'
    
    
    
    def is_code_valid(self):
        """
        Verifica si el código es válido (no expirado).
        """
        return timezone.now() < self.expiration_date and not self.verificated
