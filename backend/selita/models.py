from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    phone = models.CharField(max_length=250)
    city = models.CharField(max_length=50)

    def __str__(self):
        return (
            self.username
            + "("
            + self.first_name
            + " "
            + self.last_name
            + ")"
            + " - "
            + self.email
            + " - "
            + self.phone
            + " - "
            + self.city
        )
