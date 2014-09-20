from django.db import models

class User(models.Model):
    display_name = models.CharField(max_length=20)
    unique_name_display = models.CharField(max_length=10)
    unique_name = models.CharField(max_length=10, unique=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.unique_name_display = self.unique_name
            self.unique_name = self.unique_name.lower()
        super(User, self).save(*args, **kwargs)

class Relationship(models.Model):
    type = models.IntegerField(default=0)
    first_user = models.IntegerField()
    second_user = models.IntegerField()

    class Meta:
        unique_together = ('first_user', 'second_user')
