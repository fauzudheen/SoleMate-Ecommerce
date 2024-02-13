from django.urls import path
from . import views

app_name='user_order'

urlpatterns = [

    path('checkout_details/<int:cart_id>/', views.checkout_details, name='checkout_details'),
    path('checkout_payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout_complete/', views.checkout_complete, name='checkout_complete'),
    path('order_view/<int:order_id>/', views.order_view, name='order_view'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('razorpay-checkout/', views.razorpay_checkout, name='razorpay_checkout'),

    path('cod-payment/', views.cod_payment, name='cod_payment'),
    path('razorpay-payment/', views.razorpay_payment, name='razorpay_payment'),
    path('wallet-payment/', views.wallet_payment, name='wallet_payment'),
    path('payment/pending/', views.payment_pending, name='payment_pending'),

    path('payment/complete-pending/<int:order_item_id>', views.complete_pending_payment, name='complete_pending_payment'),
    path('cod-payment/pending', views.pending_cod_payment, name='pending_cod_payment'),
    path('razorpay-payment/pending', views.pending_razorpay_payment, name='pending_razorpay_payment'),
    path('razorpay-checkout/pending', views.pending_razorpay_checkout, name='pending_razorpay_checkout'),
    path('wallet-payment/pending', views.pending_wallet_payment, name='pending_wallet_payment'),
    path('payment/pending/pending', views.pending_payment_pending, name='pending_payment_pending'),
    path('payment/pending/complete', views.pending_payment_complete, name='pending_payment_complete'),
    path('payment/pending/failure', views.pending_payment_failure, name='pending_payment_failure'),

    path('delivery-charge/', views.apply_delivery_charge, name='apply_delivery_charge'),
    path('delivery-charge/remove/', views.remove_delivery_charge, name='remove_delivery_charge'),

]