# Generated by Django 5.0.1 on 2024-03-07 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_rename_habit1_habitrecord_habit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='lastAssessment',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
