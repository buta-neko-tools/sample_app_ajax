# Generated by Django 3.1.7 on 2021-07-05 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0013_auto_20210705_1948'),
    ]

    operations = [
        migrations.RenameField(
            model_name='searchquerymodel',
            old_name='md_newurl',
            new_name='md_old_url',
        ),
        migrations.RemoveField(
            model_name='searchquerymodel',
            name='md_oldurl',
        ),
    ]
