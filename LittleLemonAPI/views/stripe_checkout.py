import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from ..models import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart_items = Cart.objects.select_related('menuitem').filter(user=request.user)

            if not cart_items.exists():
                return Response({'error': 'El carrito está vacío'}, status=400)

            if not request.user.email:
                return Response({'error': 'El usuario no tiene un correo electrónico registrado.'}, status=400)

            line_items = []
            for item in cart_items:
                product_name = getattr(item.menuitem, 'title', 'Producto sin título')
                unit_price = int(item.unit_price * 100)

                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': unit_price,
                        'product_data': {
                            'name': product_name,
                        },
                    },
                    'quantity': item.quantity,
                })

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/success",
                cancel_url=f"{settings.FRONTEND_URL}/cancel",
                customer_email=request.user.email,
            )

            return Response({'id': checkout_session.id})

        except Exception as e:
            return Response({'error': str(e)}, status=400)


# ✅ Webhook separado y decorado correctamente
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
            Cart.objects.filter(user__email=customer_email).delete()

    return HttpResponse(status=200)