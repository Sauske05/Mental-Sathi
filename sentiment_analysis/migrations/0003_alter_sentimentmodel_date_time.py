# Generated by Django 5.1.3 on 2024-12-09 07:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sentiment_analysis", "0002_alter_sentimentmodel_date_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sentimentmodel",
            name="date_time",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 12, 9, 13, 14, 34, 932471)
            ),
        ),
    ]