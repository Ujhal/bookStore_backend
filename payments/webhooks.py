# payments/webhooks.py
import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment
from .utils import process_successful_payment  # ✅ use shared utility

@csrf_exempt
@require_POST
def razorpay_webhook(request):
    # ✅ Step 1: Verify webhook signature
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    received_signature = request.headers.get("X-Razorpay-Signature", "")

    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"),
        request.body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, received_signature):
        return HttpResponse("Invalid signature", status=400)

    # ✅ Step 2: Parse event
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON", status=400)

    event = payload.get("event")

    if event == "payment.captured":
        payment_entity = payload["payload"]["payment"]["entity"]
        razorpay_order_id = payment_entity.get("order_id")
        razorpay_payment_id = payment_entity.get("id")

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return HttpResponse("Payment not found", status=200)

        # ✅ Single call handles everything idempotently
        process_successful_payment(
            payment=payment,
            razorpay_payment_id=razorpay_payment_id
        )

    return HttpResponse("OK", status=200)