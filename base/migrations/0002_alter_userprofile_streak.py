# Generated by Django 5.0.1 on 2024-01-31 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='streak',
            field=models.IntegerField(),
        ),
    ]