import io
from datetime import datetime
from decimal import Decimal

from django.template.loader import render_to_string
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from erp.constants import TransactionType

CURRENCY_SYMBOLS = {"EUR": "€", "USD": "$", "LEK": "Lek"}

COMPANY_DEFAULTS = {
    "company_name": "ERP System",
    "company_address": "Tiranë, Shqipëri",
    "company_phone": "",
    "company_email": "",
}

STATUS_LABELS = {
    "PENDING": "Pa Paguar",
    "PARTIAL": "Paguar Pjesërisht",
    "COMPLETED": "Paguar",
    "CANCELLED": "Anuluar",
}


class InvoiceService:

    @staticmethod
    def build_context(transaction):
        from erp.models import Payment

        currency_symbol = CURRENCY_SYMBOLS.get(transaction.currency, transaction.currency)
        is_sale = transaction.transaction_type == TransactionType.SALE

        line_items = []
        subtotal = Decimal("0")
        total_tax = Decimal("0")
        has_tax = False

        if is_sale:
            items = transaction.sales.select_related("prod", "tax_rate").all()
            for item in items:
                line_total = item.prod_price * item.quantity + item.tax_amount
                subtotal += item.prod_price * item.quantity
                total_tax += item.tax_amount
                if item.tax_amount > 0:
                    has_tax = True
                line_items.append({
                    "product_name": item.prod.name,
                    "quantity": item.quantity,
                    "unit_price": f"{item.prod_price:.2f}",
                    "tax_amount": f"{item.tax_amount:.2f}",
                    "line_total": f"{line_total:.2f}",
                })
        else:
            items = transaction.restocks.select_related("prod", "tax_rate").all()
            for item in items:
                line_total = item.restock_price * item.quantity + item.tax_amount
                subtotal += item.restock_price * item.quantity
                total_tax += item.tax_amount
                if item.tax_amount > 0:
                    has_tax = True
                line_items.append({
                    "product_name": item.prod.name,
                    "quantity": item.quantity,
                    "unit_price": f"{item.restock_price:.2f}",
                    "tax_amount": f"{item.tax_amount:.2f}",
                    "line_total": f"{line_total:.2f}",
                })

        payments_qs = Payment.objects.filter(transaction=transaction).order_by("payment_date")
        total_paid = sum(p.amount for p in payments_qs)
        remaining = transaction.total_amount - total_paid

        payments = []
        for p in payments_qs:
            p_symbol = CURRENCY_SYMBOLS.get(p.currency, p.currency)
            payments.append({
                "date": p.payment_date.strftime("%d/%m/%Y %H:%M"),
                "amount": f"{p.amount:.2f}",
                "currency": p.currency,
                "currency_symbol": p_symbol,
                "method": "Cash" if p.payment_method == "CASH" else "Kartë",
                "notes": p.notes or "",
            })

        invoice_number = transaction.invoice_number or f"INV-{transaction.id:06d}"

        return {
            **COMPANY_DEFAULTS,
            "transaction_type": transaction.transaction_type,
            "invoice_number": invoice_number,
            "created_date": transaction.created_date.strftime("%d/%m/%Y"),
            "status": transaction.status,
            "status_label": STATUS_LABELS.get(transaction.status, transaction.status),
            "client": transaction.client,
            "supplier": transaction.supplier,
            "line_items": line_items,
            "has_tax": has_tax,
            "subtotal": f"{subtotal:.2f}",
            "total_tax": f"{total_tax:.2f}",
            "total_amount": f"{transaction.total_amount:.2f}",
            "total_paid": f"{total_paid:.2f}",
            "remaining": remaining,
            "currency_symbol": currency_symbol,
            "payments": payments,
            "notes": transaction.notes or "",
            "generated_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    @staticmethod
    def render_html(transaction):
        context = InvoiceService.build_context(transaction)
        return render_to_string("erp/invoice.html", context)

    @staticmethod
    def generate_pdf(transaction):
        ctx = InvoiceService.build_context(transaction)
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("InvTitle", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#2c3e50"))
        heading_style = ParagraphStyle("InvHeading", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#2c3e50"))
        normal = styles["Normal"]
        small = ParagraphStyle("Small", parent=normal, fontSize=9, textColor=colors.HexColor("#666666"))

        elements = []

        # Header
        inv_type = "FATURË" if ctx["transaction_type"] == "SALE" else "FATURË BLERJE"
        header_data = [
            [
                Paragraph(f"<b>{ctx['company_name']}</b><br/>{ctx['company_address']}", normal),
                Paragraph(
                    f"<b>{inv_type}</b><br/>Nr: {ctx['invoice_number']}<br/>Data: {ctx['created_date']}<br/>Statusi: {ctx['status_label']}",
                    ParagraphStyle("Right", parent=normal, alignment=2),
                ),
            ]
        ]
        header_table = Table(header_data, colWidths=[9 * cm, 8 * cm])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.HexColor("#2c3e50")),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 8 * mm))

        # Client/Supplier info
        party = ctx.get("client") or ctx.get("supplier")
        if party:
            label = "Klienti" if ctx["transaction_type"] == "SALE" else "Furnitori"
            party_name = f"{party.firstname} {party.lastname}"
            party_detail = party_name
            if hasattr(party, "address") and party.address:
                party_detail += f"<br/>{party.address}"
            if hasattr(party, "city") and party.city:
                party_detail += f", {party.city}"
            if hasattr(party, "phone") and party.phone:
                party_detail += f"<br/>Tel: {party.phone}"
            elements.append(Paragraph(f"<b>{label}:</b> {party_detail}", normal))
            elements.append(Spacer(1, 6 * mm))

        # Line items table
        sym = ctx["currency_symbol"]
        if ctx["has_tax"]:
            col_headers = ["#", "Produkti", "Sasia", f"Çmimi ({sym})", f"TVSH ({sym})", f"Totali ({sym})"]
            col_widths = [1 * cm, 6 * cm, 2 * cm, 3 * cm, 2.5 * cm, 3 * cm]
        else:
            col_headers = ["#", "Produkti", "Sasia", f"Çmimi ({sym})", f"Totali ({sym})"]
            col_widths = [1 * cm, 7.5 * cm, 2.5 * cm, 3 * cm, 3.5 * cm]

        table_data = [col_headers]
        for i, item in enumerate(ctx["line_items"], 1):
            row = [str(i), item["product_name"], str(item["quantity"]), item["unit_price"]]
            if ctx["has_tax"]:
                row.append(item["tax_amount"])
            row.append(item["line_total"])
            table_data.append(row)

        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        items_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        items_table.setStyle(TableStyle(items_style))
        elements.append(items_table)
        elements.append(Spacer(1, 6 * mm))

        # Totals
        totals_data = [
            ["Nëntotali:", f"{ctx['subtotal']} {sym}"],
        ]
        if ctx["has_tax"]:
            totals_data.append(["TVSH:", f"{ctx['total_tax']} {sym}"])
        totals_data.append(["TOTALI:", f"{ctx['total_amount']} {sym}"])
        totals_data.append(["Paguar:", f"{ctx['total_paid']} {sym}"])
        if ctx["remaining"] > 0:
            totals_data.append(["Mbetur:", f"{ctx['remaining']:.2f} {sym}"])

        totals_table = Table(totals_data, colWidths=[4 * cm, 4 * cm], hAlign="RIGHT")
        totals_style = [
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ]
        total_row = 2 if ctx["has_tax"] else 1
        totals_style.append(("LINEABOVE", (0, total_row), (-1, total_row), 2, colors.HexColor("#2c3e50")))
        totals_style.append(("FONTSIZE", (0, total_row), (-1, total_row), 12))
        totals_style.append(("TEXTCOLOR", (0, total_row), (-1, total_row), colors.HexColor("#2c3e50")))
        paid_row = total_row + 1
        totals_style.append(("TEXTCOLOR", (0, paid_row), (-1, paid_row), colors.HexColor("#27ae60")))
        if ctx["remaining"] > 0:
            rem_row = paid_row + 1
            totals_style.append(("TEXTCOLOR", (0, rem_row), (-1, rem_row), colors.HexColor("#e74c3c")))
        totals_table.setStyle(TableStyle(totals_style))
        elements.append(totals_table)

        # Payments history
        if ctx["payments"]:
            elements.append(Spacer(1, 8 * mm))
            elements.append(Paragraph("Historia e Pagesave", heading_style))
            pay_data = [["Data", "Shuma", "Monedha", "Mënyra", "Shënime"]]
            for p in ctx["payments"]:
                pay_data.append([p["date"], f"{p['amount']} {p['currency_symbol']}", p["currency"], p["method"], p["notes"]])
            pay_table = Table(pay_data, colWidths=[3.5 * cm, 3 * cm, 2.5 * cm, 2.5 * cm, 6 * cm], repeatRows=1)
            pay_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ecf0f1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(pay_table)

        # Notes
        if ctx["notes"]:
            elements.append(Spacer(1, 6 * mm))
            elements.append(Paragraph(f"<b>Shënime:</b> {ctx['notes']}", small))

        # Footer
        elements.append(Spacer(1, 10 * mm))
        footer = ParagraphStyle("Footer", parent=small, alignment=1)
        elements.append(Paragraph(
            f"{ctx['company_name']} — Faturë e gjeneruar automatikisht — {ctx['generated_date']}",
            footer,
        ))

        doc.build(elements)
        buf.seek(0)
        return buf
