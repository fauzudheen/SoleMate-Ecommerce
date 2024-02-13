from django.urls import path
from . import views

app_name='admin_order'

urlpatterns = [

    path('admin-home/orders/', views.orders, name='orders'),
    path('admin-home/order-items/', views.order_items, name='order_items'),
    path('admin-home/view-order/<int:order_id>/', views.view_order, name='view_order'),    

    path('admin-home/order-status/', views.order_status, name='order_status'),
    path('admin-home/order-status/unlisted/', views.unlisted_order_status, name='unlisted_order_status'),
    path('admin-home/order-status//edit/', views.add_order_status, name='add_order_status'),
    path('admin-home/order-status/edit/<int:order_status_id>/', views.edit_order_status, name='edit_order_status'),
    path('admin-home/order-status/unlist/<int:order_status_id>/', views.unlist_order_status, name='unlist_order_status'),
    path('admin-home/order-status/list/<int:order_status_id>/', views.list_order_status, name='list_order_status'),
    path('admin-home/order-items/change-status/<int:order_item_id>/', views.change_order_status, name='change_order_status'),

    path('admin-home/delivery_charge/', views.delivery_charge, name='delivery_charge'),
    path('admin-home/delivery_charge/add', views.add_delivery_charge, name='add_delivery_charge'),
    path('admin-home/delivery_charge/edit/<int:delivery_charge_id>/', views.edit_delivery_charge, name='edit_delivery_charge'),
    path('admin-home/delivery_charge/delete/<int:delivery_charge_id>/', views.delete_delivery_charge, name='delete_delivery_charge'),


]