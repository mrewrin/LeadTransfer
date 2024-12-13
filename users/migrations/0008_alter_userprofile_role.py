# Generated by Django 4.2 on 2024-12-12 20:25

from django.db import migrations, models
import django.db.models.deletion


def convert_role_to_foreign_key(apps, schema_editor):
    # Получаем модели через apps для корректной работы в миграциях
    UserProfile = apps.get_model("users", "UserProfile")
    Role = apps.get_model("users", "Role")

    # Сопоставляем строковые роли с идентификаторами ролей в таблице Role
    role_mapping = {
        "buyer": Role.objects.get_or_create(name="buyer")[0].id,
        "broker": Role.objects.get_or_create(name="broker")[0].id,
        "admin": Role.objects.get_or_create(name="admin")[0].id,
        "super_admin": Role.objects.get_or_create(name="super_admin")[0].id,
        "moderator": Role.objects.get_or_create(name="moderator")[0].id,
        "ambassador": Role.objects.get_or_create(name="ambassador")[0].id,
    }

    # Преобразуем значение поля role для каждого профиля
    for profile in UserProfile.objects.all():
        role_name = profile.role
        if role_name in role_mapping:
            profile.role_id = role_mapping[role_name]
            profile.save()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_alter_userprofile_role"),
    ]

    operations = [
        # Изменяем структуру поля role
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.ForeignKey(
                blank=True,
                help_text="Роль пользователя в системе",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_profiles",
                to="users.role",
            ),
        ),
        # Добавляем кастомную миграцию для преобразования данных
        migrations.RunPython(convert_role_to_foreign_key),
    ]