# Generated by Django 3.2 on 2024-05-22 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0186_alter_employee_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='psswd',
            field=models.CharField(default='dvczMH33lcxdW9FhGxLI', max_length=20),
        ),
    ]
