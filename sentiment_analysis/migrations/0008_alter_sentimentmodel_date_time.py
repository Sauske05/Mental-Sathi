# Generated by Django 5.1.3 on 2025-03-10 09:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sentiment_analysis", "0007_alter_sentimentmodel_date_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sentimentmodel",
            name="date_time",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 3, 10, 15, 2, 34, 966283)
            ),
        ),
    ]
