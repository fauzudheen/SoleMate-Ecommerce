from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from admin_product_management.models import Coupon, ProductVariant, UserCoupon
from user_profile.models import UserAddresses, Wallet
from user_product.models import Cart, CartItem
from .models import Order, OrderItem, OrderAddress, OrderStatus, Payment
from django.utils import timezone
import random
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import razorpay
import os
from dotenv import load_dotenv
from admin_order.models import DeliveryCharge


load_dotenv()
@never_cache
@login_required(login_url='login')
def checkout_details(request, cart_id):
    
    request.session['cart_id'] = cart_id
    addresses = UserAddresses.objects.filter(user=request.user)
    try:
        cart = Cart.objects.get(id=cart_id)
    except:
        return redirect('UserHome')

    cart.cart_total_discount = request.session.get('cart_total_discount', 0)
    cart.coupon_percent = request.session.get('coupon_percent', 0)
    cart.prediscount_cart_total = request.session.get('prediscount_cart_total', cart.total_amount)

    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        product = item.product
        size = item.product_variant
        variant = ProductVariant.objects.get(product=product, size=size)
        if variant.quantity < item.quantity:
            messages.error(request, f"The product { product.name } has only { variant.quantity } items for size { size }")
            return redirect('user_product:cart')    

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        request.session['selected_address_id'] = selected_address_id
        return redirect('user_order:checkout_payment')
    
    delivery_charges = DeliveryCharge.objects.all()
    charge_id = request.session.get('charge_id')
    delivery_charge = None 

    if charge_id:
        try:
            delivery_charge = DeliveryCharge.objects.get(id=charge_id)
        except DeliveryCharge.DoesNotExist:
            messages.warning(request, "Selected delivery charge not found. Please select a valid city.")
            return redirect('user_product:cart')
    
    return render(request, 'user_order/checkout_details.html', {
        'addresses' : addresses, 
        'cart' : cart,
        'cart_items' : cart_items,
        'delivery_charges': delivery_charges,
        'delivery_charge': delivery_charge,
        })

@never_cache
@login_required(login_url='login')
def checkout_payment(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except:
        return redirect('UserHome')
    selected_address_id = request.session['selected_address_id']

    try:
        address = UserAddresses.objects.get(id=selected_address_id)
    except:
        messages.error(request, 'Choose an address to proceed.')
        return redirect('user_order:checkout_details', cart_id=cart.id)
    
    if cart.total_amount<3000:
        try:
            charge_id = request.session['charge_id']
            delivery_charge = DeliveryCharge.objects.get(id=charge_id)
        except:
            messages.warning(request, "Select a city and click Apply for computing delivery charge")
            return redirect('user_order:checkout_details', cart_id=cart.id)

    wallet = Wallet.objects.get(user=request.user)

    cart.cart_total_discount = request.session.get('cart_total_discount', 0)
    cart.coupon_percent = request.session.get('coupon_percent', 0)
    cart.prediscount_cart_total = request.session.get('prediscount_cart_total', cart.total_amount)
    
    if cart.total_amount > 1000:
        cod = False
    else:
        cod = True
    
    return render(request, 'user_order/checkout_payment.html', {
        'address' : address, 
        'cart' : cart,
        'wallet' : wallet,
        'cod' : cod,
        })


def place_order(request, payment_method, payment_status):

    if request.method == 'POST':
        cart_id = request.session['cart_id']
        if not cart_id:
            messages.error(request, 'Cart is empty. Please add items to your cart before placing an order.')
            return redirect('user_product:cart')
        
        cart = Cart.objects.get(id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            product = item.product
            size = item.product_variant
            variant = ProductVariant.objects.get(product=product, size=size)
            if variant.quantity < item.quantity:
                messages.error(request, f"The product { product.name } has only { variant.quantity } items for size { size }")
                return redirect('user_product:cart') 
            
        if payment_method == 'Wallet':
            amount = cart.total_amount
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance >= amount:
                pass
            else:
                messages.error(request, 'Your wallet blance is insufficient to make this transaction, kindly top up your wallet')
                return "Insufficient Wallet Balance"

        cart = Cart.objects.get(id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart)
        user = request.user
        selected_address_id = request.session['selected_address_id']
        shipping_address = UserAddresses.objects.get(id=selected_address_id)

        order_address = OrderAddress.objects.create(
            full_name=shipping_address.full_name,
            street_address=shipping_address.street_address,
            city=shipping_address.city,
            district=shipping_address.district,
            state=shipping_address.state,
            pincode=shipping_address.pincode
        )

        order = Order.objects.create(
            user=user,
            address=order_address,
            total_amount=cart.total_amount, 
            order_date=timezone.now(),
        )

        for cart_item in cart_items:

            tracking_number = random.randint(1111111, 9999999)
            while OrderItem.objects.filter(tracking_number=tracking_number).exists():
                tracking_number = random.randint(1111111, 9999999)

            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_variant=cart_item.product_variant.size,
                quantity=cart_item.quantity,
                sub_total=cart_item.sub_total, 
                payment_method=payment_method,
                payment_status=payment_status,
                order_status=OrderStatus.objects.get(status='Confirmed'),
                tracking_number = tracking_number,
            )

            cart_item.product_variant.quantity -= cart_item.quantity
            cart_item.product_variant.save()

            if payment_method == 'Razorpay':
                payment = Payment.objects.create(
                        order=order,
                        amount=cart.total_amount, 
                        payment_method='Razorpay',
                        razorpay_payment_id=request.session['razorpay_payment_id']
                    )
                request.session.pop('razorpay_payment_id', None)

            if payment_method == 'Wallet':
                amount = cart.total_amount
                wallet = Wallet.objects.get(user=request.user)
                wallet.balance -= amount
                wallet.save()
                wallet.update_transaction(amount, type="Payment")
                
            
        coupon_id = request.session.get('applied_coupon_id')
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            user_coupon = UserCoupon.objects.create(user=user, coupon=coupon) 
            user_coupon.redeem_coupon()              
        else:   
            pass


        request.session.pop('cart_id', None)
        request.session.pop('selected_address_id', None)
        request.session.pop('applied_coupon_id', None)
        request.session.pop('coupon_percent', None)
        request.session.pop('cart_total_discount', None)
        request.session.pop('prediscount_cart_total', None)

        cart.delete()

        messages.success(request, 'Your order has been placed successfully!')
        return "Success"

def cod_payment(request):
    payment_method = 'Cash On Delivery'
    payment_status = 'Pending'

    order_placed = place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:checkout_complete')
    else:
        return redirect('user_order:payment_failure')


def razorpay_payment(request):
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    request.session['razorpay_payment_id'] = razorpay_payment_id  

    payment_method = 'Razorpay'
    payment_status = "Complete"

    order_placed = place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:checkout_complete')
    else:
        return redirect('user_order:payment_failure')    
    
def payment_pending(request):

    payment_method = 'Not Decided'
    payment_status = 'Pending'

    order_placed = place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:payment_failure') 
    else:
        return HttpResponse("failed")

    
def wallet_payment(request):
    payment_method = 'Wallet'
    payment_status = 'Complete'
    
    order_placed = place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:checkout_complete')
    elif order_placed == "Insufficient Wallet Balance":
        return redirect('user_order:checkout_payment')
    else:
        return redirect('user_order:payment_failure')



@never_cache
@login_required(login_url='login')
def order_view(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    address = OrderAddress.objects.get(order=order)
    return render(request, 'user_order/order_view.html', {
        'order' : order,
        'order_items' : order_items,
        'address' : address,
        })

@never_cache
@login_required(login_url='login')
def checkout_complete(request):
    return render(request, 'user_order/checkout_complete.html')

 


def razorpay_checkout(request):

    cart_id = request.session['cart_id']
    cart = Cart.objects.get(id=cart_id)

    user=request.user
    name=user.first_name
    email=user.email
    phone_no=user.phone_number
    total_amount=cart.total_amount*100

    RAZOR_KEY_ID = os.getenv('RAZOR_KEY_ID')
    RAZOR_KEY_SECRET = os.getenv('RAZOR_KEY_SECRET')

    client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
        
    payment = client.order.create({'amount': total_amount, 'currency': 'INR', 'payment_capture': 1})

    return JsonResponse({'total_amount':total_amount,
                         'name':name,
                         'email':email,
                         'phone_no':phone_no,
                         'RAZOR_KEY_ID':RAZOR_KEY_ID,
                         })


@login_required(login_url='login')
@never_cache
def payment_success(request):
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')
    
    payment = Payment.objects.create(
        razorpay_payment_id=razorpay_payment_id,
        razorpay_order_id=razorpay_order_id,
        razorpay_signature=razorpay_signature
    )
    
    return HttpResponse("Payment successful")

@never_cache
@login_required(login_url='login')
def payment_failure(request):
    return render(request, 'user_order/payment_failure.html')


def apply_delivery_charge(request):

    cart_id = request.session['cart_id']

    if request.method == 'POST':

        charge_id = request.POST.get('charge_id')
        request.session['charge_id'] = charge_id

        try:
            delivery_charge = DeliveryCharge.objects.get(id=charge_id)
            total_delivery_charge = delivery_charge.amount
        except:
            messages.warning(request, "Select a city for computing delivery charge")
            return redirect('user_order:checkout_details', cart_id)

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        charge_per_item = total_delivery_charge//len(cart_items)

        for item in cart_items:
            item.sub_total = int(item.sub_total + charge_per_item)
            item.save()
        
        cart.total_amount = sum([item.sub_total for item in cart_items])
        cart.save()

    return redirect('user_order:checkout_details', cart_id)

def remove_delivery_charge(request):
    cart_id = request.session['cart_id']
    charge_id = request.session['charge_id']

    try:
        delivery_charge = DeliveryCharge.objects.get(id=charge_id)
        total_delivery_charge = delivery_charge.amount
    except:
        messages.warning(request, "Select a city for computing delivery charge")
        return redirect('user_order:checkout_details', cart_id)

    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    charge_per_item = total_delivery_charge//len(cart_items)

    for item in cart_items:
        item.sub_total = int(item.sub_total - charge_per_item)
        item.save()
    cart.total_amount = sum([item.sub_total for item in cart_items])
    cart.save()

    request.session.pop('charge_id', None)
    
    return redirect('user_order:checkout_details', cart_id)

def complete_pending_payment(request, order_item_id):

    request.session['order_item_id'] = order_item_id

    wallet = Wallet.objects.get(user=request.user)

    try:
        order_item = OrderItem.objects.get(id=order_item_id)
    except:
        return redirect('UserHome')
    
    
    if order_item.sub_total > 1000:
        cod = False
    else:
        cod = True
    
    return render(request, 'user_order/pending_payment.html', {
        'order_item' : order_item,
        'wallet' : wallet,
        'cod' : cod,
        })

  

def pending_razorpay_checkout(request):

    order_item_id = request.session['order_item_id']
    order_item = OrderItem.objects.get(id=order_item_id)

    user=request.user
    name=user.first_name
    email=user.email
    phone_no=user.phone_number
    total_amount=order_item.sub_total*100

    RAZOR_KEY_ID = os.getenv('RAZOR_KEY_ID')
    RAZOR_KEY_SECRET = os.getenv('RAZOR_KEY_SECRET')

    client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
        
    payment = client.order.create({'amount': total_amount, 'currency': 'INR', 'payment_capture': 1})

    return JsonResponse({'total_amount':total_amount,'name':name,'email':email,'phone_no':phone_no})


def pending_razorpay_payment(request):
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    request.session['razorpay_payment_id'] = razorpay_payment_id  

    payment_method = 'Razorpay'
    payment_status = "Complete"

    order_placed = pending_place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:pending_payment_complete')
    else:
        return redirect('user_order:payment_failure')  

def pending_cod_payment(request):
    payment_method = 'Cash On Delivery'
    payment_status = 'Pending'

    order_placed = pending_place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:pending_payment_complete')
    else:
        return redirect('user_order:payment_failure')

def pending_wallet_payment(request):
    payment_method = 'Wallet'
    payment_status = 'Complete'
    
    order_placed = pending_place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:pending_payment_complete')
    else:
        return redirect('user_order:pending_payment_failure')


def pending_place_order(request, payment_method, payment_status):

    if request.method == 'POST':
        order_item_id = request.session['order_item_id']
        if not order_item_id:
            return redirect('user_prfile:orders')
        
        order_item = OrderItem.objects.get(id=order_item_id) 

        user = request.user

        if payment_method == 'Razorpay':
            payment = Payment.objects.create(
                    order=order_item.order,
                    amount=order_item.sub_total, 
                    payment_method='Razorpay',
                    razorpay_payment_id=request.session['razorpay_payment_id']
                )
            request.session.pop('razorpay_payment_id', None)

        if payment_method == 'Wallet':
            amount = order_item.sub_total
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance >= amount:
                wallet.balance -= amount
                wallet.save()
                wallet.update_transaction(amount, type="Payment")
            else:
                messages.error(request, 'Your wallet blance is insufficient to make this transaction, kindly top up your wallet')
                return "Insufficient Wallet Balance"
            
        order_item.payment_method = payment_method
        order_item.payment_status = payment_status
        order_item.save()
 
        request.session.pop('order_item_id', None)

        if payment_method == "Not Decided":
            messages.error(request, 'Your payment failed!')
        else:
            messages.success(request, 'Your payment has been completed!')

        return "Success"
    
def pending_payment_pending(request):

    payment_method = 'Not Decided'
    payment_status = 'Pending'

    order_placed = pending_place_order(request, payment_method, payment_status)
    if order_placed == "Success":
        return redirect('user_order:payment_failure') 
    else:
        return HttpResponse("failed")
    
def pending_payment_complete(request):
    return render(request, 'user_order/pending_payment_complete.html')

def pending_payment_failure(request):
    return render(request, 'user_order/pending_payment_failure.html')