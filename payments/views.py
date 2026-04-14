from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import Payment, Order
from .serializers import PaymentSerializer, CreatePaymentSerializer, PaymentVerificationSerializer
from .services import create_razorpay_order, verify_payment_signature
from orders.models import SubOrder
from orders.utils.invoice import generate_order_invoice, generate_suborder_invoice
from orders.services import reduce_book_stock
from cart.models import Cart


# payments/views.py
class CreatePaymentOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.get(id=serializer.validated_data["order_id"])

        # Check if the order amount is greater than the minimum allowed
        if order.total_amount < 1:  # Replace 1 with the actual minimum allowed amount
            return Response({
                "error": "Order amount must be greater than the minimum allowed amount."
            }, status=400)

        # Proceed to create Razorpay order
        payment, razorpay_order = create_razorpay_order(
            order=order,
        )

        return Response({
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": razorpay_order["amount"],
            "currency": "INR",
        }, status=201)

# payments/views.py

class PaymentVerificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(
            Payment,
            razorpay_order_id=serializer.validated_data["razorpay_order_id"]
        )

        # ✅ Prevent duplicate processing
        if payment.payment_status == "SUCCESS":
            return Response({"message": "Payment already verified"}, status=200)

        verified = verify_payment_signature(serializer.validated_data)

        if not verified:
            payment.payment_status = "FAILED"
            payment.save()
            return Response({"error": "Payment verification failed"}, status=400)

        # ✅ Single function handles everything idempotently
        from .utils import process_successful_payment
        process_successful_payment(
            payment=payment,
            razorpay_payment_id=serializer.validated_data["razorpay_payment_id"],
            razorpay_signature=serializer.validated_data["razorpay_signature"]
        )

        # ✅ Clear cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass

        return Response({
            "status": "Payment successful",
            "order_id": payment.order.id
        }, status=200)