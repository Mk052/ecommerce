from eshop.models import ProductOrder
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task


@shared_task
def notify_seller_new_order(product_order_id):
    
    product_order = ProductOrder.objects.filter(id=product_order_id).first()
    product = product_order.product
    subject = f"New Order Alert!"
    message = f'''Your prodcut {product.id}:{product.title}-{product.description} 
    was purchased by {product_order.buyer.email} and quantity: {product_order.quantity}'''
    from_email = settings.DEFAULT_FROM_EMAIL
    print("notify email")
    send_mail(subject, message, from_email, [product_order.product.user])