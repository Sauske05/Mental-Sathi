# Generated by Django 5.1.3 on 2025-03-10 09:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sentiment_analysis", "0006_sentimentmodel_sentiment_score_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sentimentmodel",
            name="date_time",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 3, 10, 14, 55, 55, 512696)
            ),
        ),
    ]
