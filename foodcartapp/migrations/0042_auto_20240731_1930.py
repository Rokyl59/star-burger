# Generated by Django 3.2.15 on 2023-03-02 18:59

from django.db import migrations
from django.db.models import Subquery, OuterRef


def set_price_on_order_elements(apps, schema_editor):
    OrderElement = apps.get_model('foodcartapp', 'OrderElement')
    OrderElement.objects.all().update(
        price=Subquery(
            OrderElement.objects.filter(
                pk=OuterRef('pk'),
            ).values('product__price')[:1]
        ),
    )


def move_backward(apps, schema_editor):
    OrderElement = apps.get_model('foodcartapp', 'OrderElement')
    OrderElement.objects.all().update(price=None)


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_orderelement_price'),
    ]

    operations = [
        migrations.RunPython(set_price_on_order_elements, move_backward),
    ]