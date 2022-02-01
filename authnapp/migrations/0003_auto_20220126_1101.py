# Generated by Django 3.2.11 on 2022-01-26 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authnapp', '0002_user_model_extend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopuser',
            name='activation_key',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='ключ подтверждения'),
        ),
        migrations.AlterField(
            model_name='shopuser',
            name='activation_key_expires',
            field=models.DateTimeField(blank=True, null=True, verbose_name='актуальность ключа'),
        ),
    ]
