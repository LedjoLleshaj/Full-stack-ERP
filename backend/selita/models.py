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


class Product_Categories(models.Model):
    category_name = models.CharField(max_length=200)

    class Meta:
        db_table = "product_categories"

    def __str__(self):
        return self.category_name


class Product_Names(models.Model):
    product_name = models.CharField(max_length=200)
    category_id = models.ForeignKey(Product_Categories, on_delete=models.CASCADE)

    class Meta:
        db_table = "Product_Names"

    def __str__(self):
        return self.product_name, self.category_id


class Inventory(models.Model):
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    restock_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "inventory"

    def __str__(self):
        return self.prod_id.name, self.quantity, self.restock_date


class Sales(models.Model):
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sale_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "sales"

    def __str__(self):
        return self.prod_id.name, self.quantity, self.sale_date


class Restock(models.Model):
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    restock_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "restock"

    def __str__(self):
        return self.prod_id.name, self.quantity, self.restock_date
