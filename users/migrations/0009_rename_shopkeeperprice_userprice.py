# Generated by Django 3.2.18 on 2023-07-25 18:49

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0008_remove_product_price'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ShopkeeperPrice',
            new_name='UserPrice',
        ),
    ]
