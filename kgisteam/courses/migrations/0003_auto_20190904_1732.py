# Generated by Django 2.2.5 on 2019-09-04 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20190902_2259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='worksheet',
            name='course',
        ),
        migrations.AddField(
            model_name='worksheet',
            name='course',
            field=models.ManyToManyField(to='courses.Course'),
        ),
    ]
