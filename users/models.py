from django.contrib.auth.models import AbstractUser
from django.db import models



from .managers import UserManager

class User(AbstractUser):
    username = None
    phone_number = models.CharField(
        max_length=20,
        unique=True
    )
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self):
        return self.phone_number

class Agent(models.Model):
    superviseur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='agents'
    )
    prenom = models.CharField(
        max_length=100
    )
    nom = models.CharField(
        max_length=100
    )
    telephone = models.CharField(
        max_length=20,
        blank=True
    )
    actif = models.BooleanField(
        default=True
    )
    note = models.TextField(
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    class Meta:
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
