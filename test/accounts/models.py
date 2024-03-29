from django.db import models

class Account(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

