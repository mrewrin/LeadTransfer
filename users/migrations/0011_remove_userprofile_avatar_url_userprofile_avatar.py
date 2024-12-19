# Generated by Django 4.2 on 2024-12-19 10:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0010_roleassignmenthistory"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="avatar_url",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="avatar",
            field=models.ImageField(blank=True, null=True, upload_to="avatars/"),
        ),
    ]
