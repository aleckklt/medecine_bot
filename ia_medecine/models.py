from django.db import models

class Conversation(models.Model):
    user_message = models.TextField(blank=True, null=True)
    bot_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at:%d/%m/%Y %H:%M} - {self.user_message[:50]}"


class CategorieMedecine(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.nom


class Medecin(models.Model):
    nom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.specialite})"