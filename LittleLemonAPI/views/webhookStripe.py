from decimal import Decimal
from django.contrib.auth.models import User
from ..models import Cart, Order, OrderItem
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')
        if customer_email:
            try:
                user = User.objects.get(email=customer_email)
                cart_items = Cart.objects.filter(user=user)
                if not cart_items.exists():
                    return HttpResponse(status=400)  # Carrito vacío, no crear orden

                # Calcular total
                total = sum(item.price for item in cart_items)

                # Crear orden
                order = Order.objects.create(user=user, total=total)

                # Crear items de orden
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        menuitem=item.menuitem,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        price=item.price,
                    )

                # Vaciar carrito
                cart_items.delete()

            except User.DoesNotExist:
                return HttpResponse(status=400)

    return HttpResponse(status=200)