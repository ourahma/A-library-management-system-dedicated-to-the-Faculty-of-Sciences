# Generated by Django 5.0.6 on 2024-06-21 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblio_app', '0003_signalement'),
    ]

    operations = [
        migrations.AddField(
            model_name='personne',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
