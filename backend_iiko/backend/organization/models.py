from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    authors = models.ManyToManyField('core.User', related_name='owned_organizations')

    def __str__(self):
        return self.name


class Chain(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='chains')

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.name
