# Generated by Django 3.2.15 on 2024-07-31 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20240731_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('cash', 'Наличностью'), ('online', 'Электронно')], db_index=True, default='cash', max_length=20, verbose_name='Способ оплаты'),
            preserve_default=False,
        ),
    ]