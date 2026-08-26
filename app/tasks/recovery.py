from app.core.celery_app import celery_app
import time

@celery_app.task(name="send_payment_recovery_email")
def send_payment_recovery_email(customer_email: str, customer_name: str, amount: int, order_id: str):
    """Background task to send a payment recovery reminder email to a customer."""
    print(f"[*] Sending recovery email to {customer_name} ({customer_email}) for order {order_id} (Amount: ₹{amount/100})")
    
    # Simulate email dispatch delay or integrate an SMTP / SendGrid client here
    time.sleep(2)
    
    print(f"[+] Recovery email successfully dispatched to {customer_email}!")
    return {"status": "sent", "recipient": customer_email}