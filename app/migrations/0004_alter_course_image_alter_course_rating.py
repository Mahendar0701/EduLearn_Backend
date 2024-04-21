# Generated by Django 5.0.1 on 2024-04-10 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_usercart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='rating',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
