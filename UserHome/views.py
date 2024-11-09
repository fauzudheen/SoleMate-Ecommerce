from collections import Counter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .forms import LoginForm, SignupForm, ResetPasswordForm, OtpForm, EmailForm
from .models import *
from admin_product_management.models import Category, Product, Brand, ProductVariant, Offer, ProductImages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from AdminHome.models import Banner
from django.contrib import messages 
from twilio.rest import Client
import random
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from user_product.models import WishlistItem, Cart, CartItem
from user_product.forms import AddToCartForm
from .models import OTPModel
from django.db import transaction

@never_cache
def UserHome(request):
    categories = Category.objects.filter(is_listed=True)
    brands = Brand.objects.filter(is_listed=True)
    banners = Banner.objects.all()
    products = Product.objects.filter(is_listed=True, category__is_listed=True, brand__is_listed=True)
    if request.user.is_authenticated:
        for product in products:
            product.is_added_to_wishlist = WishlistItem.objects.filter(user=request.user, product=product)
    return render(request, 'UserHome/home.html', {
        'categories': categories, 
        'products': products, 
        'brands': brands,
        'banners': banners,
    })

def signin(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Logged in successfully")
                    return redirect('UserHome')
                else:
                    messages.error(request, 'Admin has blocked this user')
            else:
                messages.error(request, "Invalid credentials")

    return render(request, 'UserHome/login.html', {'form': form})

def signup(request):
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            otp = str(random.randint(1000, 9999))
            user_data = form.cleaned_data

            with transaction.atomic():
                otp_instance = OTPModel.objects.filter(email=email).first()
                if otp_instance:
                    otp_instance.otp = otp
                    otp_instance.user_data = user_data
                    otp_instance.save()
                else:
                    otp_instance = OTPModel.objects.create(email=email, otp=otp, user_data=user_data)

            subject = 'OTP for Signup'
            message = f'Your OTP for signup is: {otp}'
            recipient = email

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)
                messages.success(request, 'Otp sent to your Gmail account')
                return redirect('otp')
            except Exception as e:
                messages.error(request, 'Failed to send OTP. Please try again.')
                return redirect('signup')

        else:
            messages.error(request, "Invalid form submission. Please check your input.")

    return render(request, 'UserHome/signup.html', {'form': form})

def otp(request):
    if request.method == 'POST':
        user_entered_otp = request.POST.get('otp')
        try:
            otp_instance = OTPModel.objects.get(otp=user_entered_otp)
            user_data = otp_instance.user_data
        except OTPModel.DoesNotExist:
            user_data = None

        if user_data and user_entered_otp == otp_instance.otp:
            form = SignupForm(user_data)
            if form.is_valid():
                form.save()
                messages.success(request, "OTP verified. Signup successful.")
                otp_instance.delete()
                return redirect('login')

        else:
            messages.error(request, "Incorrect OTP. Please try again.")
            return redirect('otp')

    return render(request, 'UserHome/otp.html')

def forgot_password(request):
    form = EmailForm()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():        
            entered_email = form.cleaned_data['email']
            user = UserProfile.objects.filter(email=entered_email)
            if user:
                subject = 'OTP for reset Password'
                message = str(random.randint(1000, 9999))
                recipient = entered_email
                send_mail(subject, 
                        message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)
                messages.success(request, 'Otp send to your gmail account')

                existing_otp_instance = OTPModel.objects.filter(email=entered_email).first()
                if existing_otp_instance and existing_otp_instance is not None:
                    existing_otp_instance.otp = message
                    existing_otp_instance.save()
                else:
                    user_data = {'key' : 'value'}
                    otp_instance = OTPModel(email=entered_email, otp=message, user_data=user_data)
                    otp_instance.save()

                return redirect('otp_for_new_password')
            else:
                messages.error(request, 'The email entered does not exist. Please try again')
    return render(request, 'UserHome/forgot-password.html', {'form' : form})

global_email = None

def otp_for_new_password(request):
    global global_email
    form = OtpForm()
    if request.method == 'POST':
        form = OtpForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            try:
                otp_instance = OTPModel.objects.filter(otp=entered_otp).first()
                email = otp_instance.email
                global_email = email
                generated_otp = otp_instance.otp if otp_instance else None

                if generated_otp == entered_otp:
                    messages.success(request, 'Otp verified')
                    return redirect('reset_password')
                else:
                    messages.error(request, 'OTP incorrect. Please try again')
            except:
                messages.error(request, 'OTP incorrect. Please try again')
    return render(request, 'UserHome/otp_for_new_password.html', {'form' : form})

def reset_password(request):
    global global_email
    form = ResetPasswordForm()
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password == confirm_password:
                user = UserProfile.objects.get(email=global_email)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed')
                return redirect('login')
            else:
                messages.error(request, 'The passwords do not match. Please try again')
    return render(request, 'UserHome/reset-password.html', {'form' : form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

@never_cache
def shop(request):
    categories = Category.objects.filter(is_listed=True)
    brands = Brand.objects.filter(is_listed=True)
    if request.method == 'POST':
        condition = request.POST['sortOption']
        products = Product.objects.filter(is_listed=True, category__is_listed=True, brand__is_listed=True)
        products = list(products)
        if condition == 'display_price':
            products.sort(key=lambda p: p.display_price)
        elif condition == '-display_price':
            products.sort(key=lambda p: p.display_price, reverse=True)
        elif condition:
            products.sort(key=lambda p: getattr(p, condition))
    else:
        products = Product.objects.filter(is_listed=True, category__is_listed=True, brand__is_listed=True)
    banners = Banner.objects.all()
    product_variants = ProductVariant.objects.all()

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(color__icontains=query)
        )

    for category in categories:
        category.active_products_count = category.product_set.filter(is_listed=True).count()
    for brand in brands:
        brand.active_products_count = brand.product_set.filter(is_listed=True).count()
    if request.user.is_authenticated:
        for product in products:
            product.is_added_to_wishlist = WishlistItem.objects.filter(user=request.user, product=product)

    sizes = [variant.size for variant in product_variants]
    variant_dict = dict(Counter(sizes))
    variant_dict = dict(sorted(variant_dict.items(), key=lambda x: int(x[0])))

    items_per_page = 9
    paginator = Paginator(products, items_per_page)
    page = request.GET.get('page')
    try:
        paginated_objects = paginator.page(page)
    except PageNotAnInteger:
        paginated_objects = paginator.page(1)
    except EmptyPage:
        paginated_objects = paginator.page(paginator.num_pages)

    return render(request, 'UserHome/shop.html', {
        'categories' : categories, 
        'paginated_objects' : paginated_objects, 
        'brands' : brands,
        'banners' : banners,
        'product_variants' : product_variants,
        'variant_dict': variant_dict,
        })

@never_cache
def product_details(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.product_variants = ProductVariant.objects.filter(product=product)
        product.available_sizes = product.product_variants.values_list('size', flat=True).distinct()
        product.images = ProductImages.objects.filter(product=product)
        
        if request.user.is_authenticated:
            product.is_added_to_wishlist = WishlistItem.objects.filter(
                user=request.user, 
                product=product
            ).exists()
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            return redirect('login')

        if request.method == 'POST':
            form = AddToCartForm(request.POST, product_id=product_id)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                selected_variant = form.cleaned_data['product_variant']
                
                # Check if item already exists in cart
                existing_cart_item = CartItem.objects.filter(
                    cart=cart,
                    product=product,
                    product_variant=selected_variant
                ).first()

                if existing_cart_item:
                    # Update existing cart item
                    existing_cart_item.quantity += quantity
                    existing_cart_item.save()
                    messages.success(request, "Cart updated successfully!")
                else:
                    # Create new cart item
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        product_variant=selected_variant,
                        quantity=quantity
                    )
                    messages.success(request, "Item added to cart!")
                
                return redirect('user_product:cart')
        else:
            form = AddToCartForm(product_id=product_id)

        context = {
            'product': product,
            'form': form,
        }
        return render(request, 'UserHome/product_details.html', context)
        
    except Product.DoesNotExist:
        messages.error(request, "Product not found!")
        return redirect('shop')

def about(request):
    brands = Brand.objects.filter(is_listed=True)
    return render(request, 'UserHome/about.html', {'brands' : brands})

def filter_product(request):
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    sizes = request.GET.getlist('size[]')
    discounts = request.GET.getlist('discount[]')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    products = Product.objects.filter(is_listed=True).distinct()

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(brands) > 0:
        products = products.filter(brand__id__in=brands).distinct()
        
    if len(sizes) > 0:
        products = [product for product in products if any(variant.size in sizes for variant in product.productvariant_set.all())]

    if min_price is not None and max_price is not None:
        try:
            min_price = int(min_price)
            max_price = int(max_price)
            products = [product for product in products if min_price <= product.display_price <= max_price]
        except ValueError:
            pass

    if len(discounts) > 0:
        min_discount = 100
        for i in discounts:
            min_discount = min(int(i), min_discount)

        products = [
                    product for product in products
                    if any(offer.percent >= min_discount for offer in Offer.objects.filter(product=product))
                ]

    data = render_to_string('UserHome/product_list.html', {'products' : products})

    return JsonResponse({'data' : data})


def cart_available_stock(request):
    if request.method == 'GET':
        cart_item_id = request.GET.get('product_id')
        quantity = request.GET.get('quantity')
        size = request.GET.get('size')

        cart_item = CartItem.objects.get(id=cart_item_id)
        product = cart_item.product
        variant = ProductVariant.objects.get(product=product, size=size)
        
        available_stock = variant.quantity

        return JsonResponse({'available_stock': available_stock})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def product_details_available_stock(request):
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        quantity = request.GET.get('quantity')
        size = request.GET.get('size')

        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.get(product=product, size=size)
        available_stock = variant.quantity


        return JsonResponse({'available_stock': available_stock})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def sort(request):
    pass