from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    role = models.CharField(max_length=200)

    class Meta:
        db_table = "users"
    
    def __str__(self):
        return self.username
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()

    class Meta:
        db_table = "product"
    
    def __str__(self):
        return self.name