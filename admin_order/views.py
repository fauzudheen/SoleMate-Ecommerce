from django.shortcuts import render, redirect
from user_order.models import Order, OrderAddress, OrderItem, OrderStatus
from user_order.forms import OrderStatusForm
from .forms import OrderStatusChangeForm
from django.contrib.auth.decorators import login_required
from AdminHome.models import DailySales
from datetime import datetime, timedelta
from .models import DeliveryCharge
from .forms import DeliveryChargeForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='AdminHome:login')
def orders(request):
    orders_list = Order.objects.all()
    
    items_per_page = 10
    paginator = Paginator(orders_list, items_per_page)
    page = request.GET.get('page')

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'admin_order/orders.html', {'orders': orders})


@login_required(login_url='AdminHome:login')
def order_items(request):
    order_items_list = OrderItem.objects.all()
    
    items_per_page = 10
    paginator = Paginator(order_items_list, items_per_page)
    page = request.GET.get('page')

    try:
        order_items = paginator.page(page)
    except PageNotAnInteger:
        order_items = paginator.page(1)
    except EmptyPage:
        order_items = paginator.page(paginator.num_pages)

    return render(request, 'admin_order/order_items.html', {'order_items': order_items})


@login_required(login_url='AdminHome:login')
def view_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'admin_order/view_order.html', {'order_items' : order_items})

@login_required(login_url='AdminHome:login')
def order_status(request):
    statuses = OrderStatus.objects.filter(is_listed=True)
    return render(request, 'admin_order/order_status.html', {'statuses' : statuses})

@login_required(login_url='AdminHome:login')
def unlisted_order_status(request):
    statuses = OrderStatus.objects.filter(is_listed=False)
    return render(request, 'admin_order/unlisted_order_status.html', {'statuses' : statuses})

@login_required(login_url='AdminHome:login')
def edit_order_status(request, order_status_id):
    status = OrderStatus.objects.get(id=order_status_id)
    form = OrderStatusForm(instance=status)

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            return redirect('admin_order:order_status')

    return render(request, 'admin_order/edit_order_status.html', {'form': form})

@login_required(login_url='AdminHome:login')
def add_order_status(request):
    form = OrderStatusForm()
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_order:order_status')
    return render(request, 'admin_order/add_order_status.html', {'form' : form})


def unlist_order_status(request, order_status_id):
    status = OrderStatus.objects.get(id=order_status_id)
    status.is_listed = False
    status.save()
    return redirect('admin_order:order_status')

def list_order_status(request, order_status_id):
    status = OrderStatus.objects.get(id=order_status_id)
    status.is_listed = True
    status.save()
    return redirect('admin_order:unlisted_order_status')

@login_required(login_url='AdminHome:login')
def change_order_status(request, order_item_id):
    order_item = OrderItem.objects.get(id=order_item_id)
    form = OrderStatusChangeForm(instance=order_item)

    if request.method == 'POST':
        form = OrderStatusChangeForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            order_item = OrderItem.objects.get(id=order_item_id)
            order_item.qty_update_on_cancel()
            order_item.add_to_sales_on_deliver()
            order_item.update_delivery_date()
            return redirect('admin_order:order_items')

    return render(request, 'admin_order/change_order_status.html', {'form': form})


@login_required(login_url='AdminHome:login')
def delivery_charge(request):
    delivery_charges = DeliveryCharge.objects.all()
    return render(request, 'admin_order/delivery_charge.html', {'delivery_charges' : delivery_charges})

@login_required(login_url='AdminHome:login')
def add_delivery_charge(request):
    form = DeliveryChargeForm()
    if request.method == 'POST':
        form = DeliveryChargeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_order:delivery_charge')
    return render(request, 'admin_order/add_delivery_charge.html', {'form' : form})

def edit_delivery_charge(request, delivery_charge_id):
    delivery_charge = DeliveryCharge.objects.filter(id=delivery_charge_id).first()
    form = DeliveryChargeForm(instance=delivery_charge)
    if request.method == 'POST':
        form = DeliveryChargeForm(request.POST, instance=delivery_charge)
        if form.is_valid():
            form.save()
            return redirect('admin_order:delivery_charge')
    return render(request, 'admin_order/add_delivery_charge.html', {'form' : form})
     
def delete_delivery_charge(request, delivery_charge_id):
    delivery_charge = DeliveryCharge.objects.filter(id=delivery_charge_id).first()
    delivery_charge.delete()
    return redirect('admin_order:delivery_charge')


