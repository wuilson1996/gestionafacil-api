# Generated by Django 3.2 on 2024-05-31 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0203_alter_employee_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='psswd',
            field=models.CharField(default='VbhLUqfI269K4QYOEj1P', max_length=20),
        ),
    ]
