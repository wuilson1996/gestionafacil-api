# Generated by Django 3.2 on 2024-04-24 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0143_alter_employee_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='psswd',
            field=models.CharField(default='MlKWu8vOrhiZOGz6a2mE', max_length=20),
        ),
    ]
