# Generated by Django 5.2 on 2025-04-28 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_employee_email_private_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='email',
            new_name='private_email',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='email_private',
            new_name='work_mail',
        ),
        migrations.RenameField(
            model_name='historicalemployee',
            old_name='email',
            new_name='private_email',
        ),
        migrations.RenameField(
            model_name='historicalemployee',
            old_name='email_private',
            new_name='work_mail',
        ),
        migrations.AlterField(
            model_name='absencerecord',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='absencerecord',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='personal_id',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalabsencerecord',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalabsencerecord',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalemployee',
            name='personal_id',
            field=models.CharField(blank=True, db_index=True, max_length=20),
        ),
    ]
