# Generated by Django 3.2 on 2024-04-26 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0159_alter_employee_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='psswd',
            field=models.CharField(default='vdKkjo3q2xfMfg3MtGuz', max_length=20),
        ),
    ]
