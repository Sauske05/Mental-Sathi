# Generated by Django 5.1.3 on 2025-03-03 08:59

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
                default=datetime.datetime(2025, 3, 3, 14, 44, 55, 893425)
            ),
        ),
    ]
