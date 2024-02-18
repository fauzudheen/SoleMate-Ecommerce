from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordChangeForm
from admin_product_management.models import Coupon, UserCoupon
from UserHome.models import UserProfile
from .forms import AddressForm, ProfileEditForm, TrackOrderForm
from .models import Referral, Transaction, UserAddresses, Wallet
from django.contrib import messages
from user_order.models import Order,OrderAddress, OrderItem, OrderStatus
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
import razorpay
import os
from dotenv import load_dotenv
import random
import string
from django.db import transaction
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@never_cache
@login_required(login_url='login')
def account(request):
    user = request.user
    return render(request, 'user_profile/account.html', {'user' : user})

@never_cache
@login_required(login_url='login')
def edit_profile(request):
    user = request.user
    form = ProfileEditForm(instance=user)
    if request.method=='POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile:account')
    return render(request, 'user_profile/edit_profile.html', {'form' : form})

@never_cache
@login_required(login_url='login')
def change_password(request):
    user = request.user
    form = PasswordChangeForm(user)
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been successfully changed.')
            return redirect('user_profile:account')
    return render(request, 'user_profile/change_password.html', {'form': form})

@never_cache
@login_required(login_url='login')
def addresses(request):
    user = request.user
    addresses = UserAddresses.objects.filter(user=user)
    return render(request, 'user_profile/addresses.html', {'addresses' : addresses})

@never_cache
@login_required(login_url='login')
def add_address(request):
    form = AddressForm()
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address_instance = form.save(commit=False)
            address_instance.user = request.user
            address_instance.save()
            return redirect('user_profile:addresses')
        else:
            messages.error(request, "Please try again.")
    return render(request, 'user_profile/add_address.html', {'form' : form})

def is_shipping(request, address_id):
    old_shipping_address = UserAddresses.objects.filter(is_shipping=True).first()

    if old_shipping_address:
        old_shipping_address.is_shipping = False
        old_shipping_address.save()

    address = UserAddresses.objects.get(id=address_id)
    address.is_shipping = True
    address.save()

    return redirect('user_profile:addresses')


def delete_address(request, address_id):
    address = UserAddresses.objects.get(id=address_id)
    address.delete()
    return redirect('user_profile:addresses')

@never_cache
@login_required(login_url='login')
def edit_address(request, address_id):
    address = UserAddresses.objects.get(id=address_id)
    form = AddressForm(instance=address)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('user_profile:addresses')
    return render(request, 'user_profile/edit_address.html', {'form' : form})

@never_cache
@login_required(login_url='login')
def orders(request):
    try:
        orders = Order.objects.filter(user=request.user)
    except Order.DoesNotExist:
        return render(request, 'user_profile/empty_orders.html')

    all_order_items = []
    for order in orders:
        order_items = OrderItem.objects.select_related('order').filter(order=order)
        all_order_items.extend(order_items)

    items_per_page = 5
    paginator = Paginator(all_order_items, items_per_page)
    page = request.GET.get('page')

    try:
        order_items = paginator.page(page)
    except PageNotAnInteger:
        order_items = paginator.page(1)
    except EmptyPage:
        order_items = paginator.page(paginator.num_pages)

    return render(request, 'user_profile/orders.html', {'order_items': order_items})

@never_cache
@login_required(login_url='login')
def all_order_items(request):
    try:
        orders = Order.objects.filter(user=request.user)
    except Order.DoesNotExist:
        return render(request, 'user_profile/empty_orders.html')
    
    all_order_items = []
    for order in orders:
        order_items = OrderItem.objects.select_related('order').filter(order=order)
        all_order_items.extend(order_items)

    items_per_page = 5
    paginator = Paginator(all_order_items, items_per_page)
    page = request.GET.get('page')

    try:
        order_items = paginator.page(page)
    except PageNotAnInteger:
        order_items = paginator.page(1)
    except EmptyPage:
        order_items = paginator.page(paginator.num_pages)
        
    return render(request, 'user_profile/all_order_items.html', {'order_items' : order_items,})


def cancel_order_item(request, order_item_id):
    order_item = OrderItem.objects.get(id=order_item_id)
    payment_status = order_item.payment_status
    if payment_status == "Complete":
        wallet = Wallet.objects.get(user=request.user)
        wallet.balance += order_item.sub_total
        wallet.save()
        wallet.update_transaction(order_item.sub_total, type="Refund")
        messages.success(request, "Order Item cancelled and amount refunded to your wallet.")
    else:
        messages.success(request, "Order Item cancelled")
    order_item.order_status = OrderStatus.objects.get(status='Cancelled')
    order_item.save()
    order_item.qty_update_on_cancel()
    return redirect('user_profile:orders')

@never_cache
@login_required(login_url='login')
def order_tracking(request):
    form = TrackOrderForm()
    order_item = None

    if request.method == 'POST':
        form = TrackOrderForm(request.POST)
        if form.is_valid():
            tracking_number = form.cleaned_data['tracking_number']
            try:
                order_item = OrderItem.objects.get(tracking_number=tracking_number)
            except OrderItem.DoesNotExist:
                order_item = "OrderItem not found"

    return render(request, 'user_profile/order_tracking.html', {'form' : form, 'order_item' : order_item})

@never_cache
@login_required(login_url='login')
def print_invoice(request, order_item_id):
    order_item = OrderItem.objects.get(id=order_item_id)
    return render(request, 'user_profile/invoice.html', {'order_item': order_item})

@never_cache
@login_required(login_url='login')
def wallet(request):
    user = request.user
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=user, balance=0)
    return render(request, 'user_profile/wallet.html', {'wallet': wallet})

@never_cache
@login_required(login_url='login')
def add_to_wallet(request):
    return render(request, 'user_profile/add_to_wallet.html')

@never_cache
@login_required(login_url='login')
def withdraw_from_wallet_view(request):
    return render(request, 'user_profile/withdraw_from_wallet.html')


def razorpay_wallet(request):
    if request.method == 'POST':
        user=request.user
        name=user.first_name
        email=user.email
        phone_no=user.phone_number
        total_amount=int(request.POST.get('amount'))*100

        RAZOR_KEY_ID = os.getenv('RAZOR_KEY_ID')
        RAZOR_KEY_SECRET = os.getenv('RAZOR_KEY_SECRET')

        client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
            
        payment = client.order.create({'amount': total_amount, 'currency': 'INR', 'payment_capture': 1})

        return JsonResponse({'total_amount':total_amount,'name':name,'email':email,'phone_no':phone_no,'RAZOR_KEY_ID':RAZOR_KEY_ID})


def razorpay_add_to_wallet(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        wallet = Wallet.objects.get(user=request.user)
        amount = int(amount)//100
        wallet.balance += amount
        wallet.save()
        wallet.update_transaction(amount, type="Deposit")
        messages.success(request, 'Amount added successfully!')
        return redirect('user_profile:wallet')

@never_cache
@login_required(login_url='login')
def withdraw_from_wallet(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        wallet = Wallet.objects.get(user=request.user)
        wallet.balance -= int(amount)
        wallet.save()
        wallet.update_transaction(amount, type="Withdraw")
    messages.success(request, 'Amount withdrawn successfully!')
    return redirect('user_profile:wallet')

@never_cache
@login_required(login_url='login') 
def transaction_history(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-id')

    paginator = Paginator(transactions, 10) 
    page_number = request.GET.get('page')

    try:
        transactions_page = paginator.page(page_number)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    return render(request, 'user_profile/transaction_history.html', {'wallet': wallet, 'transactions_page': transactions_page})


def coupon(request):
    coupons = Coupon.objects.filter(is_active=True).order_by('-expiry_date')
    for coupon in coupons:
        user_coupon = UserCoupon.objects.filter(user=request.user, coupon=coupon).first()
        expiry_date = coupon.expiry_date
        current_date = datetime.now().date()

        if user_coupon:
            coupon.status = "Redeemed"
        elif expiry_date < current_date:
            coupon.status = "Expired"
        else:
            coupon.status = "Available"
    
    user=request.user
    referral_code = user.referral_code
    referral = Referral.objects.filter(user=user).first()

    return render(request, 'user_profile/coupon.html', {
        'coupons':coupons,
        'referral_code':referral_code,
        'referral':referral,
        })

def generate_referral_code(request):
    letters_and_digits = string.ascii_letters + string.digits
    referral_code = ''.join(random.choice(letters_and_digits) for _ in range(8))

    user=request.user
    user.referral_code = referral_code
    user.save()
    
    return redirect('user_profile:coupon')

def apply_referral(request):
    if request.method == 'POST':
        entered_referral_code = request.POST['referral_code']
    
    referrer = UserProfile.objects.filter(referral_code=entered_referral_code).first() 
    referee = request.user

    if referrer and referee:
        if referrer != referee:
            with transaction.atomic():
                try:
                    referrer_wallet = Wallet.objects.get(user=referrer)
                    referee_wallet = Wallet.objects.get(user=referee)
                    
                    referrer_wallet.balance += 200
                    referee_wallet.balance += 200
                    
                    referrer_wallet.save()
                    referrer_wallet.update_transaction(amount=200, type="Referral")
                    referee_wallet.save()
                    referee_wallet.update_transaction(amount=200, type="Referral")

                    Referral.objects.create(user=referee, referral_code=entered_referral_code, is_redeemed=True)
                    messages.success(request, "Referral successful. Referral bonus of ₹200 applied.")
                except:
                    messages.error(request, "Error occured.")
        else:
            messages.warning(request, "You cannot use your own referral.")
    else:
        messages.warning(request, "Referral code is invalid.")
    return redirect('user_profile:coupon')


