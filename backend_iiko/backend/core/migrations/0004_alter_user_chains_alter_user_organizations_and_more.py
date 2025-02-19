# Generated by Django 5.1.6 on 2025-02-19 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_user_chains_user_organizations_user_restaurants'),
        ('organization', '0002_remove_organization_author_organization_authors_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='chains',
            field=models.ManyToManyField(blank=True, related_name='users', to='organization.chain'),
        ),
        migrations.AlterField(
            model_name='user',
            name='organizations',
            field=models.ManyToManyField(blank=True, related_name='users', to='organization.organization'),
        ),
        migrations.AlterField(
            model_name='user',
            name='restaurants',
            field=models.ManyToManyField(blank=True, related_name='users', to='organization.restaurant'),
        ),
    ]
