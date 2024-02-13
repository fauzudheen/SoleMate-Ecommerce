from django.urls import path
from django.shortcuts import render, redirect
from . import views

app_name='user_profile'

urlpatterns = [
    path('account/', views.account, name='account'),
    path('orders/', views.orders, name='orders'),

    path('addresses/', views.addresses, name='addresses'),
    path('addresses/add', views.add_address, name='add_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('addresses/is_shipping/<int:address_id>/', views.is_shipping, name='is_shipping'),

    path('user/account/edit', views.edit_profile, name='edit_profile'),
    path('user/account/change-password', views.change_password, name='change_password'),

    path('order-tracking/', views.order_tracking, name='order_tracking'),
    path('all_order_items/', views.all_order_items, name='all_order_items'),
    path('cancel_order_item/<int:order_item_id>', views.cancel_order_item, name='cancel_order_item'),

    path('print-invoice/<int:order_item_id>/', views.print_invoice, name='print_invoice'),

    path('wallet/', views.wallet, name='wallet'),
    path('wallet/add/', views.add_to_wallet, name='add_to_wallet'),
    path('razorpay-wallet/', views.razorpay_wallet, name='razorpay_wallet'),
    path('razorpay-wallet/add/', views.razorpay_add_to_wallet, name='razorpay_add_to_wallet'),
    path('wallet/withdraw/', views.withdraw_from_wallet, name='withdraw_from_wallet'),
    path('wallet/withdrw/', views.withdraw_from_wallet_view, name='withdraw_from_wallet_view'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),

    path('user/coupon/', views.coupon, name='coupon'),
    path('referal', views.generate_referral_code, name='generate_referral_code'),
    path('referal/apply', views.apply_referral, name='apply_referral'),

]

