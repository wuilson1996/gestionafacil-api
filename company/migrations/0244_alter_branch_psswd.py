# Generated by Django 3.2 on 2024-07-02 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0243_alter_branch_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='psswd',
            field=models.CharField(default='SnrMhEOpPs', max_length=10),
        ),
    ]
