# Generated by Django 3.2 on 2024-05-09 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0187_auto_20240509_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='seriefolio',
            name='next_folio',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='branch',
            name='psswd',
            field=models.CharField(default='KzvcbfrNp6', max_length=10),
        ),
    ]
