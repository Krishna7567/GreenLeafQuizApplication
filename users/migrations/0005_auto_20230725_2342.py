# Generated by Django 3.2.18 on 2023-07-25 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_staffprice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='updated_by',
        ),
        migrations.AddField(
            model_name='product',
            name='staff_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
