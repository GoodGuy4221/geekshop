# Generated by Django 3.2.11 on 2022-01-26 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authnapp', '0004_alter_shopuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopuser',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email'),
        ),
    ]