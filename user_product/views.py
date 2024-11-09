from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Cart, CartItem, WishlistItem
from .forms import AddToCartForm
from django.core.exceptions import ObjectDoesNotExist
from admin_product_management.models import Coupon, Product, Offer, UserCoupon
from django.http import JsonResponse, HttpResponse
from django.contrib import messages 
from admin_order.models import DeliveryCharge
from datetime import datetime
from django.http import JsonResponse

@never_cache
@login_required(login_url='login')
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.select_related('product').filter(cart=cart)

        for cart_item in cart_items:
            cart_item.save_dup() # This will recalculate the subtotal

        cart.total_amount = sum(item.sub_total for item in cart_items)
        cart.save()

        cart.cart_total_discount = request.session.get('cart_total_discount', 0)
        cart.coupon_percent = request.session.get('coupon_percent', 0)
        cart.prediscount_cart_total = request.session.get('prediscount_cart_total', cart.total_amount)

        for cart_item in cart_items:
            cart_item.product.is_added_to_wishlist = WishlistItem.objects.filter(
                product=cart_item.product,
                user=request.user
            ).exists()

        try:
            id = request.session.get('applied_coupon_id')
        except KeyError:
            id = None
        coupon = Coupon.objects.filter(id=id).first()
        
        request.session.pop('charge_id', None)

        if cart_items:
            return render(request, 'user_product/cart.html', {
                'cart_items': cart_items,
                'cart': cart,
                'coupon': coupon,
                })
        else:
            return render(request, 'user_product/empty_cart.html')

    except ObjectDoesNotExist:
        return render(request, 'user_product/empty_cart.html')



def add_to_cart(request):
    pass


def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()

    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart.total_amount = sum(item.sub_total for item in cart_items)
    cart.save()

    return JsonResponse({'status': 'success', 'updated_total_amount': cart.total_amount})


def update_cart_item_quantity(request):
    if request.method == 'POST':

        item_id = int(request.POST.get('item_id'))
        new_quantity = int(request.POST.get('new_quantity'))

        if new_quantity > 0:
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.quantity = new_quantity
            cart_item.save_dup()
            
            updated_subtotal = cart_item.sub_total

            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            cart.total_amount = sum(item.sub_total for item in cart_items)
            cart.save()
            updated_total_amount = cart.total_amount
            
            return JsonResponse({'status': 'success', 'updated_subtotal': updated_subtotal, 'updated_total_amount': updated_total_amount})
        else:
            return JsonResponse({'status': 'error'})

def clear_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    cart.delete()
    return redirect('user_product:cart')

@never_cache
@login_required(login_url='login')
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'user_product/wishlist.html', {'wishlist_items': wishlist_items})



def add_to_wishlist(request, product_id):
    product_to_be_added = get_object_or_404(Product, id=product_id)
    existing_product = WishlistItem.objects.filter(user=request.user, product=product_to_be_added)

    if existing_product:
        return JsonResponse({'status': 'error', 'message': 'Product already exists in Wishlist'})
    else:
        wishlist_item = WishlistItem(
            user=request.user,
            product=product_to_be_added,
        )
        wishlist_item.save()
        return JsonResponse({'status': 'success'})




def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    wishlist_item.delete()
    return JsonResponse({'status': 'success'})




def downloads(request):
    return render(request, 'user_product/account-downloads.html')

@never_cache
@login_required(login_url='login')
def payment_methods(request):
    return render(request, 'user_product/account-payment-methods.html')

def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        coupon = Coupon.objects.filter(code=code).first()
        if coupon:
            if coupon.is_active:
                percent = coupon.discount_percent
                cart = Cart.objects.get(user=request.user)
                cart_total_discount = int(cart.total_amount*(percent / 100))
                total = cart.total_amount

                redeemed_coupon = UserCoupon.objects.filter(user=request.user, coupon=coupon).first()
                if not redeemed_coupon:
                    expiry_date = coupon.expiry_date
                    current_date = datetime.now().date()
                    if expiry_date < current_date:
                        messages.error(request, 'This coupon has been expired.')
                    else:
                        if total < coupon.min_price or total > coupon.max_price:
                            messages.error(request, f'To apply this coupon, total cart amount should be in the range ₹{coupon.min_price} - ₹{coupon.max_price}')
                        else:
                            request.session['applied_coupon_id'] = coupon.id
                            request.session['coupon_percent'] = percent
                            request.session['cart_total_discount'] = cart_total_discount
                            request.session['prediscount_cart_total'] = cart.total_amount
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.sub_total = int(item.sub_total - int((percent / 100) * item.sub_total))
                                item.save()
                            messages.success(request, 'Coupon code applied')
                else:
                    messages.error(request, 'This coupon has been already redeemed')
            else:
                messages.error(request, 'The coupon has expired')
        else:
            messages.error(request, 'Coupon with the entered code does not exist')
    return redirect('user_product:cart')  

def remove_coupon(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart)
    for item in cart_items:
        item.save_dup()
        
    request.session.pop('applied_coupon_id', None)
    request.session.pop('coupon_percent', None)
    request.session.pop('cart_total_discount', None)
    request.session.pop('prediscount_cart_total', None)

    messages.success(request, 'Coupon removed')
    return redirect('user_product:cart')  






