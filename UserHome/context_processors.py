from admin_product_management.models import Product, Category
from user_product.models import Cart, CartItem
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

def base_context(request):
    name = "Guest" 
    user = request.user

    if user.is_authenticated:  
        first_name = user.first_name 
        last_name = user.last_name 
        name = f"{first_name} {last_name}"      

    return {'name': name}

def cart_number_context(request):
    cart_number = 0
    if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_number = len(cart_items)
        except Cart.DoesNotExist:
            pass  

    return {'cart_no': cart_number}

def category_context(request):
    categories = Category.objects.filter(is_listed=True)
    return {'categoriesss': categories}


def product_context(request, product_id):
    product = Product.objects.get(id=product_id)
    return {'product' : product}



