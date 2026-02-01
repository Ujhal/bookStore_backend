import razorpay
from django.conf import settings
from django.utils.crypto import get_random_string
from decimal import Decimal
from .models import Payment

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def create_razorpay_order(order):
    # Calculate amounts from order
    amount = order.total_amount
    gst = 0  # or calculate GST if needed

    razorpay_order = client.order.create({
        "amount": int(amount * 100) + int(gst * 100),
        "currency": settings.RAZORPAY_CURRENCY,
        "payment_capture": settings.RAZORPAY_PAYMENT_CAPTURE,
    })

    payment = Payment.objects.create(
        order=order,
        book_amount=amount,
        gst=gst,
        total_amount=amount + gst,
        transaction_id=razorpay_order['id'],
        razorpay_order_id=razorpay_order['id'],
    )

    return payment, razorpay_order


def verify_payment_signature(data):
    try:
        client.utility.verify_payment_signature(data)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
