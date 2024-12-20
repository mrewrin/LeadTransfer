# Generated by Django 4.2 on 2024-12-12 11:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("properties", "0005_alter_realestateobject_broker"),
    ]

    operations = [
        migrations.AlterField(
            model_name="realestateobject",
            name="features",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Дополнительные характеристики объекта",
            ),
        ),
        migrations.AlterField(
            model_name="realestateobject",
            name="photos",
            field=models.JSONField(
                blank=True, default=list, help_text="Ссылки на фотографии"
            ),
        ),
        migrations.AlterField(
            model_name="realestateobject",
            name="videos",
            field=models.JSONField(
                blank=True, default=list, help_text="Ссылки на видео"
            ),
        ),
    ]
