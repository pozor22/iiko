from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Kitchen(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE)
    stop = models.BooleanField(default=False)
    count = models.PositiveIntegerField(default=1)

    def buy_stop(self):
        if self.stop:
            self.count -= 1
            self.save()

    def save(self, *args, **kwargs):
        if self.count < 1:
            self.stop = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
