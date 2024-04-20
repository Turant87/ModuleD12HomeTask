# Generated by Django 4.2.11 on 2024-04-20 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_category_subscribers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='subscribers',
        ),
        migrations.RemoveField(
            model_name='post',
            name='postCategory',
        ),
        migrations.AddField(
            model_name='post',
            name='postCategory',
            field=models.ManyToManyField(related_name='posts', to='news.category'),
        ),
    ]
