# Generated by Django 5.0.1 on 2024-04-25 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_module_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='enrolledStudents',
            field=models.IntegerField(default=0),
        ),
    ]
