from collections import defaultdict
from orders.services import reduce_book_stock
from orders.utils.invoice import generate_order_invoice, generate_suborder_invoice
from orders.models import SubOrder  # wherever SubOrder lives

def process_successful_payment(payment, razorpay_payment_id, razorpay_signature=None):
    """
    Idempotent. Safe to call from both webhook and frontend verify.
    """
    if payment.payment_status == "SUCCESS":
        return  # Already handled

    payment.payment_status = "SUCCESS"
    payment.razorpay_payment_id = razorpay_payment_id
    if razorpay_signature:
        payment.razorpay_signature = razorpay_signature
    payment.save()

    order = payment.order
    order.status = "Confirmed"
    order.transaction_id = payment.transaction_id
    order.save(update_fields=["status", "transaction_id"])

    reduce_book_stock(order)

    if not order.sub_orders.exists():
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

        try:
            generate_order_invoice(order)
            for suborder in suborders:
                generate_suborder_invoice(suborder)
        except Exception as e:
            print(f"[Invoice Error] {e}")