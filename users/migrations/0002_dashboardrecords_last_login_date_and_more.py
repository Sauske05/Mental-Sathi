# Generated by Django 5.1.3 on 2025-03-03 08:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="dashboardrecords",
            name="last_login_date",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 3, 3, 14, 15, 38, 587901)
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 3, 3, 14, 15, 38, 586901)
            ),
        ),
    ]
