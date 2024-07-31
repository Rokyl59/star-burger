# Generated by Django 3.2.15 on 2023-03-02 18:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20240731_1921'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderelement',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена'),
        ),
    ]