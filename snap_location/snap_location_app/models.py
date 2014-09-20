from django.db import models

class User(models.Model):
    display_name = models.CharField(max_length=20)
    unique_name = models.CharField(max_length=10, unique=True)

class Relationship(models.Model):
    type = models.IntegerField(default=0)
    first_user = models.IntegerField()
    second_user = models.IntegerField()

    class Meta:
        unique_together = ('first_user', 'second_user')
