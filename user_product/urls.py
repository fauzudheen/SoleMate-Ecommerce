from django.urls import path
from . import views

app_name='user_product'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('cart/add', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update-quantity/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('downloads/', views.downloads, name='downloads'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),

    path('coupon-apply/', views.apply_coupon, name='apply_coupon'),
    path('coupon-remove/', views.remove_coupon, name='remove_coupon'),
    
    
]