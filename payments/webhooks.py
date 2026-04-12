# payments/webhooks.py
import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from collections import defaultdict
from .models import Payment
from orders.models import Order, SubOrder
from orders.services import reduce_book_stock
from orders.utils.invoice import generate_order_invoice, generate_suborder_invoice

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
            # Nothing we can do, but return 200 so Razorpay stops retrying
            return HttpResponse("Payment not found", status=200)

        # ✅ Step 3: Idempotency check — don't process twice
        if payment.payment_status == "SUCCESS":
            return HttpResponse("Already processed", status=200)

        # ✅ Step 4: Mark payment successful
        payment.payment_status = "SUCCESS"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.save()

        order = payment.order
        order.status = "Confirmed"
        order.transaction_id = payment.transaction_id
        order.save(update_fields=["status", "transaction_id"])

        # ✅ Step 5: Reduce stock
        reduce_book_stock(order)

        # ✅ Step 6: Create SubOrders (only if not already created)
        if not order.suborders.exists():
            items_by_stakeholder = defaultdict(list)
            for order_item in order.order_items.all():
                items_by_stakeholder[order_item.book.created_by].append(order_item)

            suborders = []
            for publisher, items in items_by_stakeholder.items():
                suborder = SubOrder.objects.create(
                    order=order,
                    publisher=publisher,
                    status="Confirmed"
                )
                suborders.append(suborder)

            # ✅ Step 7: Generate invoices
            try:
                generate_order_invoice(order)
                for suborder in suborders:
                    generate_suborder_invoice(suborder)
            except Exception:
                pass  # Log but don't fail — payment is already confirmed

    return HttpResponse("OK", status=200)