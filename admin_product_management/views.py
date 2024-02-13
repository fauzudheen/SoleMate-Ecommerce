from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from admin_product_management.models import Coupon
from .forms import CategoryForm, Category, BrandForm, ProductForm, ProductVariantForm, OfferForm, CouponForm
from django.contrib import messages
from .models import Category, Brand, Product, ProductVariant, Offer, ProductImages
from django.db.models import Q, F
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# ---BRAND---
@login_required(login_url='AdminHome:login')
def brand(request):
    brands = Brand.objects.filter(is_listed=True)
    return render(request, 'admin_product_management/brand.html', {'brands' : brands})

@login_required(login_url='AdminHome:logi')
def add_brand(request):
    form = BrandForm()
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Added Brand')
            return JsonResponse({'redirect_url': reverse('admin_product_management:brand')})
        else:
            return JsonResponse({'error': 'Form is not valid'})
    return render(request, 'admin_product_management/add_brand.html', {'form': form})

@login_required(login_url='AdminHome:login')
def edit_brand(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('admin_product_management:brand')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'admin_product_management/edit_brand.html', {'form': form, 'brand': brand})

@login_required(login_url='AdminHome:login')
def unlisted_brands(request):
    brands = Brand.objects.filter(is_listed=False)
    return render(request, 'admin_product_management/unlisted_brands.html', {'brands' : brands})

def list_brand(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    brand.is_listed = True
    brand.save()
    return redirect('admin_product_management:unlisted_brands')

def unlist_brand(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    brand.is_listed = False
    brand.save()
    return redirect('admin_product_management:brand')
# ---CATEGORY---

@login_required(login_url='AdminHome:login')
def category(request):
    categories = Category.objects.filter(is_listed=True)
    return render(request, 'admin_product_management/category.html', {'categories' : categories})

@login_required(login_url='AdminHome:login')
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Added Category')
            return JsonResponse({'redirect_url': reverse('admin_product_management:category')})
        else:
            return JsonResponse({'error': 'Form is not valid'})

    return render(request, 'admin_product_management/add_category.html', {'form': form})

@login_required(login_url='AdminHome:login')
def edit_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_product_management:category')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_product_management/edit_category.html', {'form': form, 'category': category})

@login_required(login_url='AdminHome:login')
def unlisted_categories(request):
    categories = Category.objects.filter(is_listed=False)
    return render(request, 'admin_product_management/unlisted_categories.html', {'categories' : categories})

def list_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.is_listed = True
    category.save()
    return redirect('admin_product_management:unlisted_categories')

def unlist_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.is_listed = False
    category.save()
    return redirect('admin_product_management:category')
# ---PRODUCT---

from django.db.models import Q

@login_required(login_url='AdminHome:login')
def product(request):

    query = request.GET.get('q')
    products = Product.objects.filter(is_listed=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(color__icontains=query)
        )

    for product in products:
        product.offer = Offer.objects.filter(product=product).first()
        product.variants = ProductVariant.objects.filter(product=product)

    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    try:
        paginated_objects = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_objects = paginator.page(1)
    except EmptyPage:
        paginated_objects = paginator.page(paginator.num_pages)


    return render(request, 'admin_product_management/product.html', {'paginated_objects': paginated_objects})


@login_required(login_url='AdminHome:login')
def add_product(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save()
            product_images = request.FILES.getlist('images')
            if product_images:
                for img in product_images:
                    ProductImages.objects.create(product=new_product, images = img)
            return JsonResponse({'redirect_url': reverse('admin_product_management:product')})
        else:
            return JsonResponse({'error': 'Form is not valid'})
    return render(request, 'admin_product_management/add_product.html', {'form': form})

@login_required(login_url='AdminHome:login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    existing_images = ProductImages.objects.filter(product=product)
    product.variants = ProductVariant.objects.filter(product=product)
    product.offers = Offer.objects.filter(product=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_product = form.save()
            product_images = request.FILES.getlist('images')
            if product_images:
                for img in product_images:
                    ProductImages.objects.create(product=new_product, images = img)
            return redirect('admin_product_management:product')
        else:
            return JsonResponse({'error': 'Form is not valid'})
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_product_management/edit_product.html', {
        'form': form,
        'existing_images' : existing_images,
        'product' : product,
         })

@login_required(login_url='AdminHome:login')
def view_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.offer = Offer.objects.filter(product=product).first()
    product.variants = ProductVariant.objects.filter(product=product)
    product.images = ProductImages.objects.filter(product=product)
    return render(request, 'admin_product_management/view_product.html', {'product' : product})

def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.is_listed = False
    product.save()
    return redirect('admin_product_management:product')

@login_required(login_url='AdminHome:login')
def deleted_product(request):
    products = Product.objects.filter(is_listed=False)
    print(products)
    return render(request, 'admin_product_management/deleted_product.html', {'products': products})

def restore_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.is_listed=True
    product.save()
    return redirect('admin_product_management:deleted_product')

# ---PRODUCT IMAGE---
def delete_image(request, image_id):
    image_to_delete = ProductImages.objects.get(id=image_id)
    product_id = image_to_delete.product.id
    image_to_delete.delete()
    return redirect(reverse('admin_product_management:edit_product', kwargs={'product_id': product_id}))


# ---PRODUCT VARIENT---

@login_required(login_url='AdminHome:login')
def add_product_variant(request, product_id):
    form = ProductVariantForm()
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES)
        if form.is_valid():
            product = product
            size = form.cleaned_data['size']
            quantity = form.cleaned_data['quantity']
            existing_variant = ProductVariant.objects.filter(size=size, product=product).exists()
            if existing_variant:
                ProductVariant.objects.filter(size=size,product=product).update(quantity=F('quantity')+quantity)
            else:
                form.instance.product = product
                form.save()
            return redirect(reverse('admin_product_management:edit_product', kwargs={'product_id': product_id}))

    return render(request, 'admin_product_management/add_product_variant.html', {'form': form, 'product': product})

@login_required(login_url='AdminHome:login')
def edit_product_variant(request, product_variant_id):
    product_variant = get_object_or_404(ProductVariant, pk=product_variant_id)
    product = product_variant.product 
    product_id = product_variant.product.id
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES, instance=product_variant)
        if form.is_valid():
            form.save()
        return redirect(reverse('admin_product_management:edit_product', kwargs={'product_id': product_id}))

    else:
        form = ProductVariantForm(instance=product_variant)
    return render(request, 'admin_product_management/edit_product_variant.html', {'form': form, 'product': product})

def delete_product_variant(request, product_variant_id):
    product_variant = get_object_or_404(ProductVariant, pk=product_variant_id)
    product_variant.delete()
    product_id = product_variant.product.id
    return redirect(reverse('admin_product_management:edit_product', kwargs={'product_id': product_id}))



# ---OFFER---

@login_required(login_url='AdminHome:login')
def add_offer(request, product_id):
    form = OfferForm(initial={'product': product_id})
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.product_id = product_id
            offer.save()
            return redirect(reverse('admin_product_management:edit_product', kwargs={'product_id': product_id}))
    return render(request, 'admin_product_management/add_offer.html', {'form': form, 'product': product})

@login_required(login_url='AdminHome:login')
def edit_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    product = offer.product
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            product_id = offer.product.id
            return redirect(reverse('admin_product_management:edit_product', kwargs={'product_id': product_id}))
    else:
        form = OfferForm(instance=offer)
    return render(request, 'admin_product_management/edit_offer.html', {'form': form, 'product': product})

def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    offer.delete()
    product_id = offer.product.id
    return redirect(reverse('admin_product_management:edit_product', kwargs={'product_id': product_id}))

@login_required(login_url='AdminHome:login')
def coupon(request):
    coupons = Coupon.objects.filter(is_active=True).order_by('-expiry_date')
    return render(request, 'admin_product_management/coupon.html', {'coupons': coupons})

@login_required(login_url='AdminHome:login')
def add_coupon(request):
    form = CouponForm()
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_product_management:coupon')
    return render(request, 'admin_product_management/add_coupon.html', {'form': form,})

@login_required(login_url='AdminHome:login')
def edit_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    form = CouponForm(instance=coupon)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('admin_product_management:coupon')
    return render(request, 'admin_product_management/edit_coupon.html', {'form': form})

def deactivate_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.is_active = False
    coupon.save()
    return redirect('admin_product_management:coupon')

def activate_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.is_active = True
    coupon.save()
    return redirect('admin_product_management:coupon')

@login_required(login_url='AdminHome:login')
def deactivated_coupons(request):
    coupons = Coupon.objects.filter(is_active=False)
    return render(request, 'admin_product_management/deactivated_coupons.html', {'coupons': coupons,})