# Generated by Django 4.2.7 on 2023-11-23 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0002_income_rainy_day_fund'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='income',
            options={},
        ),
        migrations.RemoveField(
            model_name='income',
            name='rainy_day_fund',
        ),
    ]
