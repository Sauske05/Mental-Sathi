# Generated by Django 5.1.3 on 2024-12-12 08:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sentiment_analysis", "0004_alter_sentimentmodel_date_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sentimentmodel",
            name="date_time",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 12, 12, 14, 18, 2, 395960)
            ),
        ),
    ]