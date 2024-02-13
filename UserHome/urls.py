from django.urls import path
from . import views

urlpatterns = [
    path('User/', views.UserHome, name='UserHome'),
    path('shop/', views.shop, name='shop'),
    path('', views.signin, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('otp/', views.otp, name='otp'),
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('about/', views.about, name='about'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('otp-new-password/', views.otp_for_new_password, name='otp_for_new_password'),
    path('filter-product/', views.filter_product, name='filter_product'),
    path('cart_available_stock/', views.cart_available_stock, name='cart_available_stock'),
    path('product_details_available_stock/', views.product_details_available_stock, name='product_details_available_stock'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('sort/', views.sort, name='sort'),
    
    
]
