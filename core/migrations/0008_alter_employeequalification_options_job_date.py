# Generated by Django 4.2.1 on 2024-06-12 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_appnotification_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employeequalification',
            options={'verbose_name': 'Employee Experience', 'verbose_name_plural': 'Employee Experiences'},
        ),
        migrations.AddField(
            model_name='job',
            name='Date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
