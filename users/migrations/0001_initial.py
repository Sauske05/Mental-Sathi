# Generated by Django 5.1.3 on 2024-11-26 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "user_name",
                    models.CharField(max_length=120, primary_key=True, serialize=False),
                ),
                ("password", models.CharField(max_length=120)),
                ("email", models.CharField(max_length=120)),
            ],
        ),
    ]