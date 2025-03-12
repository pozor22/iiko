from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    restaurant = models.ManyToManyField('organization.Restaurant', related_name='categories')

    def __str__(self):
        return self.name


class Kitchen(models.Model):
    name = models.CharField(max_length=255, unique=True)
    restaurant = models.ManyToManyField('organization.Restaurant', related_name='kitchens')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    count = models.IntegerField(default=0)
    restaurant = models.ForeignKey('organization.Restaurant', on_delete=models.CASCADE, related_name='ingredients')

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.PositiveIntegerField(default=1)
    stop = models.BooleanField(default=False)
    count = models.PositiveIntegerField(default=None, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE)
    restaurant = models.ManyToManyField('organization.Restaurant', related_name='products')

    def buy(self):
        if not self.count is None:
            self.count -= 1
            self.save()

    def save(self, *args, **kwargs):
        if self.count < 1:
            self.stop = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recipes')
    ingredient = models.ManyToManyField(Ingredient, related_name='recipes')
    quantity = models.PositiveIntegerField(default=1)
    measure = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.product} - {self.ingredient}'
