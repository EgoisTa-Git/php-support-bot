# Generated by Django 4.1.7 on 2023-02-25 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_tg_id_squashed_0004_alter_customuser_tg_id_squashed_0005_alter_customuser_tg_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='bot_state',
            field=models.CharField(blank=True, help_text='Стейт машина', max_length=50, verbose_name='Текущее состояния бота'),
        ),
    ]