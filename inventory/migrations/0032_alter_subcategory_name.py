# Generated by Django 3.2 on 2024-07-22 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0031_product_image_b64'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]
