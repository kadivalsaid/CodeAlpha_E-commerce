from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Cart, CartItem, Order, OrderItem, Product


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def home(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'store/home.html', {'products': products})


def product_detail(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})


@login_required
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related('product').all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})


@login_required
@require_POST
def add_to_cart(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_or_create_cart(request.user)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save(update_fields=['quantity'])

    messages.success(request, f'Added "{product.name}" to cart.')
    return redirect('cart')


@login_required
@require_POST
def update_cart_item(request, item_id: int):
    cart = _get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    try:
        qty = int(request.POST.get('quantity', '1'))
    except ValueError:
        qty = 1

    if qty <= 0:
        item.delete()
    else:
        item.quantity = qty
        item.save(update_fields=['quantity'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_total = float(cart.total())
        return JsonResponse(
            {
                'ok': True,
                'item_id': item_id,
                'cart_total': cart_total,
            }
        )

    return redirect('cart')


@login_required
@require_POST
def remove_cart_item(request, item_id: int):
    cart = _get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()

    messages.info(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def checkout(request):
    cart = _get_or_create_cart(request.user)
    items = list(cart.items.select_related('product').all())
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('home')

    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        address = (request.POST.get('address') or '').strip()
        city = (request.POST.get('city') or '').strip()
        postal_code = (request.POST.get('postal_code') or '').strip()

        if not (full_name and email and address and city and postal_code):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'store/checkout.html', {'cart': cart, 'items': items})

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            postal_code=postal_code,
            paid=True,
        )

        OrderItem.objects.bulk_create(
            [
                OrderItem(order=order, product=ci.product, price=ci.product.price, quantity=ci.quantity)
                for ci in items
            ]
        )

        cart.items.all().delete()
        messages.success(request, 'Order placed successfully!')
        return redirect('order_success', order_id=order.id)

    return render(request, 'store/checkout.html', {'cart': cart, 'items': items})


@login_required
def order_success(request, order_id: int):
    try:
        order = Order.objects.prefetch_related('items__product').get(pk=order_id, user=request.user)
    except Order.DoesNotExist as exc:
        raise Http404 from exc
    return render(request, 'store/order_success.html', {'order': order})
