
from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Product, Order, UserProfile
from .forms import ProductForm


# =====================================
# 1. PRODUCT LIST
# =====================================

def product_list(request):

    products = Product.objects.all().order_by('-id')

    return render(request, 'shop/product_list.html', {
        'products': products
    })


# =====================================
# 2. PRODUCT DETAIL + RECENTLY VIEWED
# =====================================

def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    recently_viewed = request.session.get(
        'recently_viewed', []
    )

    product_id = product.id

    if product_id in recently_viewed:
        recently_viewed.remove(product_id)

    recently_viewed.insert(0, product_id)

    # Store only latest 5 products
    request.session['recently_viewed'] = recently_viewed[:5]

    return render(request, 'shop/product_detail.html', {
        'product': product
    })


# =====================================
# 3. ADD TO CART (SESSION)
# =====================================

def add_to_cart(request, product_id):

    if request.method != 'POST':
        return redirect('product_list')

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity >= product.stock:

        messages.error(request, 'Insufficient stock')

        return redirect('view_cart')

    cart[product_id] = current_quantity + 1

    request.session['cart'] = cart

    messages.success(request, 'Product added to cart')

    return redirect('view_cart')


# =====================================
# 4. VIEW CART (SESSION)
# =====================================

def view_cart(request):

    cart = request.session.get('cart', {})

    cart_items = []

    total = Decimal('0.00')

    for product_id, quantity in cart.items():

        product = Product.objects.filter(
            id=product_id
        ).first()

        if product is None:
            continue

        subtotal = product.price * quantity

        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# =====================================
# 5. REMOVE FROM CART
# =====================================

def remove_from_cart(request, product_id):

    if request.method != 'POST':
        return redirect('view_cart')

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart

    messages.success(request, 'Product removed from cart')

    return redirect('view_cart')


# =====================================
# 6. RECENTLY VIEWED PRODUCTS
# =====================================

def recently_viewed_products(request):

    product_ids = request.session.get(
        'recently_viewed', []
    )

    products = Product.objects.filter(
        id__in=product_ids
    )

    return render(request, 'shop/recently_viewed.html', {
        'products': products
    })


# =====================================
# 7. CREATE PRODUCT
# =====================================

@staff_member_required
def product_create(request):

    form = ProductForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():

        form.save()

        messages.success(request, 'Product created successfully')

        return redirect('product_list')

    return render(request, 'shop/product_form.html', {
        'form': form
    })


# =====================================
# 8. UPDATE PRODUCT
# =====================================

@staff_member_required
def product_update(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product
    )

    if request.method == 'POST' and form.is_valid():

        form.save()

        messages.success(request, 'Product updated successfully')

        return redirect('product_list')

    return render(request, 'shop/product_form.html', {
        'form': form
    })


# =====================================
# 9. DELETE PRODUCT
# =====================================

@staff_member_required
def product_delete(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':

        product.delete()

        messages.success(request, 'Product deleted successfully')

        return redirect('product_list')

    return render(request, 'shop/product_confirm_delete.html', {
        'product': product
    })


# =====================================
# 10. USER PROFILE
# =====================================

@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')

        profile.save()

        messages.success(request, 'Profile updated successfully')

        return redirect('profile_view')

    return render(request, 'shop/profile.html', {
        'profile': profile
    })


# =====================================
# 11. ORDER HISTORY
# =====================================

@login_required
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        'items__product'
    ).order_by('-created_at')

    return render(request, 'shop/order_list.html', {
        'orders': orders
    })
