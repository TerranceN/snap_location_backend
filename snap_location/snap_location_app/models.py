from django.db import models

class User(models.Model):
    display_name = models.CharField(max_length=20)
    unique_name_display = models.CharField(max_length=10)
    unique_name = models.CharField(max_length=10, unique=True)
    score = models.IntegerField(default=0)
    images_sent = models.IntegerField(default=0)
    images_received = models.IntegerField(default=0)

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

class GameRound(models.Model):
    sender = models.IntegerField()
    recipient = models.IntegerField()
    datetime = models.DateTimeField(db_index=True)
    image_data = models.IntegerField()
    gps_latitude = models.FloatField()
    gps_longitude = models.FloatField()

class UploadedImage(models.Model):
    reference_count = models.IntegerField()
    image_data = models.FileField()
