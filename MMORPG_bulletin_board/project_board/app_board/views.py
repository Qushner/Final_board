from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ValidationError

from PIL import Image

from accounts.models import CustomUser as User
from .models import Listing, Reply
from .forms import ListingForm, ReplyForm


class ListingsAll(ListView):

    model = Listing
    ordering = '-dateCreation'
    template_name = 'listings_all.html'
    context_object_name = 'listings'
    paginate_by = 10

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        user = self.request.user
        listings = context['listings']
        has_user_reply = []
        for listing in listings:
            if user.is_authenticated:
                has_user_reply.append({
                    'listing': listing,
                    'has_reply': Reply.objects.filter(listing=listing, author=user).exists()
                })
            else:
                has_user_reply.append({
                    'listing': listing,
                    'has_reply': False
                })
        context['has_user_reply'] = has_user_reply
        context['time_now'] = timezone.localtime(timezone.now())
        return context


class ListingDetail(DetailView):

    model = Listing
    template_name = 'listing.html'
    context_object_name = 'listing'
    queryset = Listing.objects.all()

    @staticmethod
    def resize_image(image_field, new_width, new_height):

        image_path = image_field.path
        image = Image.open(image_path)
        image = image.resize((new_width, new_height))
        image.save(image_path)  # Сохранение измененного изображения на диск

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        listing = self.get_object()
        user = self.request.user

        context['has_user_reply'] = Reply.objects.filter(listing=listing, author=user).exists()

        # Изменение размеров изображения image1, если файл существует
        if listing.image1 and listing.image1.file:
            self.resize_image(listing.image1, 400, 300)

        # Изменение размеров изображения image2, если файл существует
        if listing.image2 and listing.image2.file:
            self.resize_image(listing.image2, 400, 300)

        context['listing'] = listing
        return context


class CreateListing(LoginRequiredMixin, CreateView):

    permission_required = ('listings.add_listing',)
    form_class = ListingForm
    model = Listing
    template_name = 'listing_create.html'

    def form_valid(self, form):
        listing = form.save(commit=False)
        listing.author = self.request.user

        # Обработка и сохранение файлов изображений
        image1 = self.request.FILES.get('image1')
        image2 = self.request.FILES.get('image2')
        if image1:
            listing.image1 = image1
        if image2:
            listing.image2 = image2

        try:
            listing.full_clean()  # Проверка валидности модели
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

        return super().form_valid(form)


class EditListing(LoginRequiredMixin, UpdateView):

    permission_required = ('listings.change_listing',)
    form_class = ListingForm
    model = Listing
    template_name = 'listing_edit.html'


class DeleteListing(LoginRequiredMixin, DeleteView):

    permission_required = ('listings.delete_listing',)
    model = Listing
    template_name = 'listing_delete.html'
    success_url = reverse_lazy('listings_all')


class AuthorListings(LoginRequiredMixin, ListingsAll):

    model = Listing
    template_name = 'author_list.html'
    context_object_name = 'listings'

    def get_queryset(self):
        self.author = get_object_or_404(User, id=self.kwargs['pk'])
        queryset = Listing.objects.filter(author=self.author).order_by('-dateCreation')
        return queryset


class ReplyDetail(DetailView):

    model = Reply
    template_name = 'reply.html'
    context_object_name = 'reply'
    queryset = Reply.objects.all()


class ListingReply(ListView):

    model = Reply
    template_name = 'reply_list.html'
    context_object_name = 'replies'

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Reply.objects.filter(listing_id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        listing = Listing.objects.get(id=pk)
        context['listing'] = listing
        return context


class ReplyCreate(LoginRequiredMixin, CreateView):

    permission_required = ('reply.add_reply',)
    form_class = ReplyForm
    model = Reply
    template_name = 'reply_create.html'

    def form_valid(self, form):
        reply = form.save(commit=False)
        listing_id = self.kwargs['pk']
        reply.listing_id = listing_id
        reply.author = self.request.user
        reply.save()

        listing = Listing.objects.get(id=listing_id)
        listing.has_user_reply = True
        listing.save()

        return super().form_valid(form)

    def get_success_url(self):
        listing = Listing.objects.get(id=self.kwargs['pk'])
        return listing.get_absolute_url()


class AuthorReplies(LoginRequiredMixin, ListView):

    model = Reply
    template_name = 'author_replies.html'
    context_object_name = 'author_replies'

    def get_queryset(self):
        self.author = get_object_or_404(User, id=self.kwargs['pk'])
        queryset = Reply.objects.filter(author=self.author)
        return queryset


@login_required
@csrf_protect
def accept_reply(request, pk):

    reply = get_object_or_404(Reply, id=pk)
    reply.status = True
    reply.save()
    message = 'Вы приняли отклик'
    return render(request, 'action.html', {'reply': reply.text, 'message': message})


@login_required
@csrf_protect
def reject_reply(request, pk):

    reply = get_object_or_404(Reply, id=pk)
    reply.delete()
    message = 'Вы отклонили отклик. Отклик удален!'
    return render(request, 'action.html', {'reply': reply.text, 'message': message})


@login_required
@csrf_protect
def cancel_reply(request, pk):

    reply = get_object_or_404(Reply, id=pk)
    reply.status = False
    reply.save()

    # Отправка email-уведомления пользователю, решение по отклику которого было  отозвано
    email = reply.author.email
    subject = 'Решение по вашему отклику отозвано.'
    text_content = (
        f'Отклик: {reply.text}\n'
        f'На объявление: {reply.listing.title}\n\n'
        f'Автору объявления нужно больше времени для принятия решения!'
    )
    html_content = (
        f'Отклик: {reply.text}<br>'
        f'На объявление: {reply.listing.title}<br><br>'
        f'Автору объявления нужно больше времени для принятия решения!'
    )

    msg = EmailMultiAlternatives(subject, text_content, None, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    message = 'Вы передумали и отозвали решение по отклику.'
    return render(request, 'action.html', {'reply': reply.text, 'message': message})


@login_required
@csrf_protect
def reply_action(request, pk):

    if request.method == 'POST':
        reply_id = request.POST.get('reply_id')
        reply = get_object_or_404(Reply, id=reply_id)
        action = request.POST.get('action')

        if action == 'accept':
            reply.status = True
            reply.save()
        elif action == 'reject':
            reply.delete()
        elif action == 'cancel':
            reply.status = False
            reply.save()

            # Отправка email-уведомления пользователю, решение по отклику которого было  отозвано
            email = reply.author.email
            subject = 'Решение по вашему отклику отозвано.'
            text_content = (
                f'Отклик: {reply.text}\n'
                f'На объявление: {reply.listing.title}\n\n'
                f'Автору объявления нужно больше времени для принятия решения!'
            )
            html_content = (
                f'Отклик: {reply.text}<br>'
                f'На объявление: {reply.listing.title}<br><br>'
                f'Автору объявления нужно больше времени для принятия решения!'
            )

            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    replies = Reply.objects.filter(listing__author=request.user)
    return render(request, 'reply_action.html', {'replies': replies})
