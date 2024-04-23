from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Post

@receiver(post_save, sender=Post)
def send_new_post_notification(sender, instance, created, **kwargs):
    if created:
        categories = instance.postCategory.all()
        for category in categories:
            for user in category.subscribers.all():
                subject = instance.title
                html_message = render_to_string('mail_template.html', {
                    'title': instance.title,
                    'text': instance.text[:50],
                    'username': user.username
                })
                plain_message = strip_tags(html_message)
                from_email = 'From <turant.ivan@yandex.ru>'
                to = user.email

                send_mail(subject, plain_message, from_email, [to], html_message=html_message)