from rest_framework import serializers
from .models import Payment
from orders.models import Order


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "book_amount",
            "gst",
            "total_amount",
            "payment_status",
            "refund_status",
            "refund_msg",
            "razorpay_order_id",
            "razorpay_payment_id",
            "transaction_id",
            "created_at",
        ]


class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Invalid order ID")

        if hasattr(order, "payment"):
            raise serializers.ValidationError("Payment already exists for this order")

        if order.status != "Pending":
            raise serializers.ValidationError("Order is not eligible for payment")

        return value


class PaymentVerificationSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
