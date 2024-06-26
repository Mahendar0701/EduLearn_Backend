# Generated by Django 5.0.1 on 2024-04-14 07:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_course_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='app.category'),
            preserve_default=False,
        ),
    ]
