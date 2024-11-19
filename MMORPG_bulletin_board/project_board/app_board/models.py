from django.db import models
from django.urls import reverse

from accounts.models import CustomUser as User


class Listing(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    dateCreation = dateCreation = models.DateTimeField(auto_now_add=True)
    CATEGORY_CHOICES = (
        ('tank', 'Танки'),
        ('healer', 'Хилы'),
        ('dd', 'ДД'),
        ('trader', 'Торговцы'),
        ('guild_master', 'Гилдмастеры'),
        ('quest_giver', 'Квестгиверы'),
        ('blacksmith', 'Кузнецы'),
        ('leatherworker', 'Кожевники'),
        ('alchemist', 'Зельевары'),
        ('spellcaster', 'Мастера заклинаний'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100)
    text = models.TextField()
    image1 = models.ImageField(blank=True)
    image2 = models.ImageField(blank=True)

    def get_category_display_ru(self):
        category_choices = dict(self.CATEGORY_CHOICES)
        return category_choices.get(self.category, '')

    def get_absolute_url(self):
        return reverse('listing_detail', args=[str(self.id)])


class Reply(models.Model):

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.BooleanField(default=False)
