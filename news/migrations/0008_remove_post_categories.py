# Generated by Django 4.2.11 on 2024-04-20 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_post_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='categories',
        ),
    ]
