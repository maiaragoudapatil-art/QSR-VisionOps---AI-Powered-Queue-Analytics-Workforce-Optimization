import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import LiveAnalytics


def export_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Customers",
        "Queue Length",
        "Wait Time",
        "Occupancy",
        "Created At",
    ])

    analytics = LiveAnalytics.objects.all()

    for item in analytics:
        writer.writerow([
            item.customer_count,
            item.queue_length,
            item.average_wait_time,
            item.occupancy,
            item.created_at,
        ])

    return response


def export_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="report.pdf"'
    )

    p = canvas.Canvas(response)

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawString(
        100,
        800,
        "QSR VisionOps Report"
    )

    y = 760

    analytics = LiveAnalytics.objects.all()[:20]

    for item in analytics:

        p.drawString(
            50,
            y,
            f"Customers: {item.customer_count} | "
            f"Queue: {item.queue_length} | "
            f"Wait: {item.average_wait_time} | "
            f"Occupancy: {item.occupancy}"
        )

        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response
