from django.db.models.signals import post_save, post_delete
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver

from .models import Reply



@receiver(post_save, sender=Reply)
def notify_new_reply(instance, created, **kwargs):
    if created:
        email = instance.listing.author.email
        subject = 'Новый отклик на объявление'
        text_content = (
            f'Новый отклик: {instance.text}\n'
            f'На объявление: {instance.listing.title}\n\n'
            f'Ссылка на отклик: http://127.0.0.1:8000/reply/{instance.id}'
        )
        html_content = (
            f'Новый отклик: {instance.text}<br>'
            f'На объявление: {instance.listing.title}<br><br>'
            f'<a href="http://127.0.0.1:8000/reply/{instance.id}">'
            f'Ссылка на отклик</a>'
        )
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()



@receiver(post_save, sender=Reply)
def notify_reply_accept(instance, **kwargs):
    email = instance.author.email
    if instance.status:

        subject = 'Ваш отклик принят'
        text_content = (
            f'Отклик: {instance.text}\n'
            f'На объявление: {instance.listing.title}\n\n'
            f'принят аввтором объявления'
        )
        html_content = (
            f'Отклик: {instance.text}<br>'
            f'На объявление: {instance.listing.title}<br><br>'
            f'принят автором объявления'
        )

        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()



@receiver(post_delete, sender=Reply)
def notify_reply_reject(instance, **kwargs):
    email = instance.author.email
    subject = 'Отклит отклонен'
    text_content = (
        f'Отклик: {instance.text}\n'
        f'На объявление: {instance.listing.title}\n\n'
        f'Ваш отклик отклонен и удален!'
    )
    html_content = (
        f'Отклик: {instance.text}<br>'
        f'На объявление: {instance.listing.title}<br><br>'
        f'Ваш отклик отклонен и удален!'
    )
    msg = EmailMultiAlternatives(subject, text_content, None, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
