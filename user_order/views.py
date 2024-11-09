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
            messages.warning(request, "Select a city and click Apply in the bottom for computing delivery charge")
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
        print(f"Received Cart ID: {cart_id}")  
        
        if not cart_id:
            messages.error(request, 'Cart is empty. Please add items to your cart before placing an order.')
            return redirect('user_product:cart')
        
        cart = Cart.objects.get(id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart)
        print(f"Cart Items: {cart_items}")  
        
        for item in cart_items:
            product = item.product
            size = item.product_variant
            variant = ProductVariant.objects.get(product=product, size=size)
            print(f"Checking stock for product {product.name}, size {size}: available {variant.quantity}, requested {item.quantity}")  # Debugging stock check
            if variant.quantity < item.quantity:
                messages.error(request, f"The product {product.name} has only {variant.quantity} items for size {size}")
                return redirect('user_product:cart')

        if payment_method == 'Wallet':
            amount = cart.total_amount
            print(f"Wallet payment selected. Total amount: {amount}")  
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance >= amount:
                print("Sufficient wallet balance.")  
            else:
                messages.error(request, 'Your wallet balance is insufficient to make this transaction, kindly top up your wallet')
                return "Insufficient Wallet Balance"

        # Place the order
        print(f"Placing order for user: {request.user}")  
        user = request.user
        selected_address_id = request.session['selected_address_id']
        shipping_address = UserAddresses.objects.get(id=selected_address_id)
        print(f"Shipping Address: {shipping_address}")  

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
        print(f"Order created with ID: {order.id}")  

        if payment_method == 'Razorpay':
            razorpay_payment_id = request.session.get('razorpay_payment_id')
            print(f"Razorpay Payment ID from session: {razorpay_payment_id}")
            
            if not razorpay_payment_id:
                messages.error(request, 'Payment ID not found in session')
                return "Payment ID Missing"
                
            payment = Payment.objects.create(
                order=order,
                amount=cart.total_amount,
                payment_method='Razorpay',
                razorpay_payment_id=razorpay_payment_id
            )
            print(f"Payment created with ID: {payment.id}")
            request.session.pop('razorpay_payment_id', None)

        # Create order items
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
                tracking_number=tracking_number,
            )
            print(f"Order item created with tracking number: {tracking_number}")

          
            cart_item.product_variant.quantity -= cart_item.quantity
            cart_item.product_variant.save()

        # Handle wallet payment after order items are created
        if payment_method == 'Wallet':
            amount = cart.total_amount
            wallet = Wallet.objects.get(user=request.user)
            wallet.balance -= amount
            wallet.save()
            wallet.update_transaction(amount, type="Payment")

        # Handle coupon
        coupon_id = request.session.get('applied_coupon_id')
        print(f"Applied Coupon ID: {coupon_id}")
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            user_coupon = UserCoupon.objects.create(user=user, coupon=coupon)
            user_coupon.redeem_coupon()

        # Clear session data
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
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=400)

    try:
        # Get payment details from POST data
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Validate required parameters
        if not all([payment_id, order_id, signature]):
            raise ValueError("Missing required payment parameters")

        # Initialize Razorpay client
        client = razorpay.Client(auth=(os.getenv('RAZOR_KEY_ID'), os.getenv('RAZOR_KEY_SECRET')))

        # Verify payment signature
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        
        client.utility.verify_payment_signature(params_dict)
        print("Payment signature verified")

        request.session['razorpay_payment_id'] = payment_id 

        # If signature verification passes, process the order
        payment_method = 'Razorpay'
        payment_status = "Complete"
        
        order_result = place_order(request, payment_method, payment_status)
        
        if order_result == "Success":
            # Clean up session data
            for key in ['razorpay_order_id', 'razorpay_payment_id']:
                request.session.pop(key, None)
                
            return JsonResponse({
                'status': 'success',
                'message': 'Payment processed successfully'
            })
        else:
            raise ValueError("Order placement failed")

    except razorpay.errors.SignatureVerificationError as e:
        print(f"Signature verification failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Payment verification failed'
        }, status=400)
        
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
    
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
    try:
        cart_id = request.session.get('cart_id')
        if not cart_id:
            raise ValueError("Cart ID not found in session")
            
        cart = Cart.objects.get(id=cart_id)
        user = request.user
        
        total_amount = int(cart.total_amount * 100)
        
        RAZOR_KEY_ID = os.getenv('RAZOR_KEY_ID')
        RAZOR_KEY_SECRET = os.getenv('RAZOR_KEY_SECRET')
        client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
        
        order_data = {
            'amount': total_amount,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'cart_id': str(cart_id),
                'user_id': str(user.id)
            }
        }
        
        payment = client.order.create(order_data)
        
        request.session['razorpay_order_id'] = payment['id']
        request.session.modified = True
        
        return JsonResponse({
            'status': 'success',
            'total_amount': total_amount,
            'name': user.first_name,
            'email': user.email,
            'phone_no': user.phone_number,
            'RAZOR_KEY_ID': RAZOR_KEY_ID,
            'order_id': payment['id']
        })
        
    except Exception as e:
        print(f"Error in razorpay_checkout: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


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