# Generated by Django 5.1.6 on 2025-02-21 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_remove_organization_author_organization_authors_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chain',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
