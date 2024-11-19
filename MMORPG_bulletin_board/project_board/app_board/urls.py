from django.urls import path
from .views import (ListingsAll, ListingDetail, CreateListing,
                    EditListing, DeleteListing, AuthorListings, ListingReply, ReplyCreate, AuthorReplies, accept_reply,
                    reject_reply, reply_action, ReplyDetail, cancel_reply)

urlpatterns = [
    path('listings/', ListingsAll.as_view(), name='listings_all'),
    path('listings/<int:pk>', ListingDetail.as_view(), name='listing_detail'),
    path('reply/<int:pk>', ReplyDetail.as_view(), name='reply_detail'),
    path('listings/create/', CreateListing.as_view(), name='listing_create'),
    path('listings/<int:pk>/edit/', EditListing.as_view(), name='listing_edit'),
    path('listings/<int:pk>/delete/', DeleteListing.as_view(), name='listing_delete'),
    path('user/<int:pk>', AuthorListings.as_view(), name='author_list'),
    path('user/<int:pk>/replies', AuthorReplies.as_view(), name='author_replies'),
    path('listings/<int:pk>/replies', ListingReply.as_view(), name='replies'),
    path('listings/<int:pk>/reply_create', ReplyCreate.as_view(), name='reply_create'),
    path('accept_reply/<int:pk>/', accept_reply, name='accept_reply'),
    path('reject_reply/<int:pk>/', reject_reply, name='reject_reply'),
    path('cancel_reply/<int:pk>/', cancel_reply, name='cancel_reply'),
    path('user/<int:pk>/reply_action/', reply_action, name='reply_action'),
]