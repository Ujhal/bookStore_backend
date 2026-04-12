from django.urls import path
from .views import CreatePaymentOrderAPIView, PaymentVerificationAPIView
from .webhooks import razorpay_webhook  

urlpatterns = [
    path("create/", CreatePaymentOrderAPIView.as_view()),
    path("verify/", PaymentVerificationAPIView.as_view()),
    path("webhook/", razorpay_webhook),

]
