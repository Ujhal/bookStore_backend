from django.urls import path
from .views import CreatePaymentOrderAPIView, PaymentVerificationAPIView

urlpatterns = [
    path("create/", CreatePaymentOrderAPIView.as_view()),
    path("verify/", PaymentVerificationAPIView.as_view()),
]
