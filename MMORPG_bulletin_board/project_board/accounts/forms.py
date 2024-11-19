from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser as User
from django.core.mail import EmailMultiAlternatives

import random


class SignUpForm(UserCreationForm):

    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        if commit:
            user.save()

            verification_code = random.randint(1000, 9999)
            user.verification_code = verification_code
            self.instance.verification_code = verification_code
            self.instance.save()
            self.send_verification_email(user.email, verification_code, user.id)

        return user

    def send_verification_email(self, email, verification_code, pk):
        subject = "Код подтверждения для регистрации на MMORG Community"
        text = f"Для завершения регистрации на странице подтверждения введите следующий код: {verification_code}"
        html = f"<p>Для завершения регистрации на странице подтверждения <a href='http://127.0.0.1:8000/accounts/verify/{pk}/'>введите следующий код</a>: <strong>{verification_code}</strong></p>"
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()


class VerificationForm(forms.Form):
    verification_code = forms.IntegerField(label="Код подтверждения")
