from django.urls import path
from .views import SignUp, VerificationView

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('verify/<int:pk>/', VerificationView.as_view(), name='verification'),
]