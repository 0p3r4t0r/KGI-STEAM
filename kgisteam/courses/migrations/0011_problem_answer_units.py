# Generated by Django 2.2.6 on 2019-10-29 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_populate_calculated_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='answer_units',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]