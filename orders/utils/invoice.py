from django.template.loader import get_template
from django.core.files.base import ContentFile
from io import BytesIO
from xhtml2pdf import pisa


def render_to_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)

    result = BytesIO()
    pisa_status = pisa.CreatePDF(
        src=html,
        dest=result
    )

    if pisa_status.err:
        raise Exception("Error generating PDF")

    return result
def generate_order_invoice(order):
    pdf = render_to_pdf(
        "invoices/order_invoice.html",
        {
            "order": order,
            "items": order.order_items.all(),
        }
    )

    filename = f"order_invoice_{order.id}.pdf"
    order.invoice_pdf.save(
        filename,
        ContentFile(pdf.getvalue()),
        save=True
    )
def generate_suborder_invoice(suborder):
    items = suborder.order.order_items.filter(
        book__created_by=suborder.publisher
    )

    pdf = render_to_pdf(
        "invoices/suborder_invoice.html",
        {
            "suborder": suborder,
            "items": items,
        }
    )

    filename = f"suborder_invoice_{suborder.id}.pdf"
    suborder.invoice_pdf.save(
        filename,
        ContentFile(pdf.getvalue()),
        save=True
    )
