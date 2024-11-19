from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    verification_code = models.IntegerField(default=0)
