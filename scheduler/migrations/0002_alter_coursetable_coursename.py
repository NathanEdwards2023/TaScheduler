# Generated by Django 5.0.4 on 2024-04-19 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursetable',
            name='courseName',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
