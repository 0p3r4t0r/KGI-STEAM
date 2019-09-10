from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_solution_release_datetime_20190910_2113'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CourseResource',
        ),
        migrations.DeleteModel(
            name='Resource',
        ),
    ]
