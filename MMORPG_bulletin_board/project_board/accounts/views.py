from django.contrib import messages
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .models import CustomUser as User
from .forms import VerificationForm, SignUpForm


class SignUp(CreateView):

    model = User
    form_class = SignUpForm

    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse('verification', kwargs={'pk': self.object.pk})


class VerificationView(View):


    def get(self, request, pk):
        form = VerificationForm()
        return render(request, 'registration/verification.html', {'form': form, 'pk': pk})

    def post(self, request, pk):
        form = VerificationForm(request.POST)
        if form.is_valid():
            verification_code = form.cleaned_data.get('verification_code')
            user = User.objects.get(id=pk)
            if verification_code == user.verification_code:
                user.is_active = True
                user.save()
                return redirect('login')
            else:
                messages.error(request, "Неверный код подтверждения.")
            return render(request, 'registration/verification.html', {'form': form, 'pk': pk})
