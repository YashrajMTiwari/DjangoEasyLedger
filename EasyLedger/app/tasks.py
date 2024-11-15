from celery import shared_task

from EasyLedger.app.views import send_payment_pending_notification
from .models import Purchase

@shared_task
def check_and_notify_pending_payments_task():
    # Your logic to check and notify pending payments
    pending_purchases = Purchase.objects.filter(payment_status='pending')
    for purchase in pending_purchases:
        send_payment_pending_notification(purchase.customer)
