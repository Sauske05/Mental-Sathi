# Generated by Django 5.1.3 on 2025-03-08 02:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("sessions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Chat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.CharField(max_length=255)),
                ("assistant_text", models.TextField()),
                ("user_query", models.TextField()),
                ("date_time", models.DateTimeField(auto_now_add=True)),
                (
                    "session_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sessions.session",
                    ),
                ),
            ],
        ),
    ]
