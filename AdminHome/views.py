import io
import json
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import LoginForm, BannerForm
from django.contrib import messages
from .models import Admin, Banner, DailySales
from UserHome.models import UserProfile
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from user_order.models import OrderItem, Order
from django.db.models import Sum
from admin_product_management.models import Product
from UserHome.models import UserProfile
from django.template.loader import render_to_string
from django.db.models import Count, Q


@login_required(login_url='AdminHome:login')
def home(request):
    admin = request.user

    if not admin.is_superuser:
        return redirect('UserHome')

    data = {}

    order_items = OrderItem.objects.filter(order_status=4)
    data['total_revenue'] = order_items.aggregate(total_revenue=Sum('sub_total'))['total_revenue']
    data['total_users'] = len(UserProfile.objects.all())
    data['total_products'] = len(Product.objects.all())
    data['total_orders'] = len(OrderItem.objects.all())
    data['orders_completed'] = len(OrderItem.objects.filter(order_status=4))
    data['orders_pending'] = len(OrderItem.objects.exclude(order_status=4))
    data['top_three_products'] = OrderItem.objects.filter(order_status=4).values('product__name').annotate(total_orders=Count('id')).order_by('-total_orders')[:3]
    data['top_three_categories'] = OrderItem.objects.filter(order_status=4).values('product__category__name').annotate(total_orders=Count('id')).order_by('-total_orders')[:3]
    data['top_three_brands'] = OrderItem.objects.filter(order_status=4).values('product__brand__name').annotate(total_orders=Count('id')).order_by('-total_orders')[:3]

    return render(request, 'AdminHome/dashboard.html', { 'admin' : admin, 'data': data})


def login_view(request):
    if request.user.is_superuser:
        return redirect('AdminHome:home')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    messages.success(request, "Logged in successfully as admin")
                    return redirect('AdminHome:home')
                else:
                    messages.error(request, 'You are not an admin')
            else:
                messages.error(request, "Invalid credentials")

    return render(request, 'AdminHome/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('AdminHome:login')


# ---BANNER---

@login_required(login_url='AdminHome:login')
def banner(request):
    banners = Banner.objects.all()
    return render(request, 'AdminHome/banner.html', {'banners' : banners})

@login_required(login_url='AdminHome:login')
def add_banner(request):
    form = BannerForm()
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Added Banner')
            return redirect('AdminHome:banner')
    return render(request, 'AdminHome/add_banner.html', {'form': form})

@login_required(login_url='AdminHome:login')
def edit_banner(request, banner_id):
    banner = get_object_or_404(Banner, pk=banner_id)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('AdminHome:banner')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'AdminHome/edit_banner.html', {'form': form})

def delete_banner(request, banner_id):
    banner = get_object_or_404(Banner, pk=banner_id)
    banner.delete()
    return redirect('AdminHome:banner')


# ---USERS---

@login_required(login_url='AdminHome:login')
def users(request):
    users = UserProfile.objects.all()

    for user in users:
        user.full_name = f"{user.first_name}  {user.last_name}"
    return render(request, 'AdminHome/users.html', {'users' : users})

def block_user(request, user_id):
    user_to_be_blocked = UserProfile.objects.get(id=user_id)
    user_to_be_blocked.is_active = False
    user_to_be_blocked.save()
    return redirect('AdminHome:users')

def unblock_user(request, user_id):
    user_to_be_unblocked = UserProfile.objects.get(id=user_id)
    user_to_be_unblocked.is_active = True
    user_to_be_unblocked.save()
    return redirect('AdminHome:users')

def delete_user(request, user_id):
    user = UserProfile.objects.get(id=user_id)
    user.delete()
    return redirect('AdminHome:users')

def daily_sales_page(request):
    return render(request,'AdminHome/daily_sales.html')

def weekly_sales_page(request):
    return render(request,'AdminHome/weekly_sales.html')

def monthly_sales_page(request):
    return render(request,'AdminHome/monthly_sales.html')



def get_sales_data(start_date, end_date, frequency='daily'):
    sales_data = {}

    current_date = start_date

    while current_date <= end_date:
        if frequency == 'daily':
            sales = OrderItem.objects.filter(order__order_date=current_date, order_status=4)
        elif frequency == 'weekly':
            week_start = current_date - timedelta(days=current_date.weekday())
            week_end = week_start + timedelta(days=6)
            sales = OrderItem.objects.filter(order__order_date__range=(week_start, week_end), order_status=4)
            current_date = week_end + timedelta(days=1)
        elif frequency == 'monthly':
            month_start = current_date.replace(day=1)
            month_end = month_start.replace(day=1) + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            sales = OrderItem.objects.filter(order__order_date__range=(month_start, month_end), order_status=4)
            current_date = month_end + timedelta(days=1)

        total_sales = sum(entry.sub_total for entry in sales)
        sales_data[current_date.strftime('%Y-%m-%d')] = total_sales
        current_date += timedelta(days=1)

    dates = list(sales_data.keys())
    sales = list(sales_data.values())

    return dates, sales

def daily_sales(request):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)

    dates, sales = get_sales_data(start_date, end_date)
    return JsonResponse({'dates': dates, 'sales': sales})

def weekly_sales(request):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(weeks=19)

    dates, sales = get_sales_data(start_date, end_date, frequency='weekly')
    return JsonResponse({'dates': dates, 'sales': sales})

def monthly_sales(request):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=364)

    dates, sales = get_sales_data(start_date, end_date, frequency='monthly')
    return JsonResponse({'dates': dates, 'sales': sales})


def calculate_sales_report(order_items):
    sales_report_data = {}

    sales_report_data['items_sold'] = len(order_items)
    sales_report_data['revenue'] = sum(item.sub_total for item in order_items)

    best_selling_product = order_items.values('product').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold').first()

    if best_selling_product:
        product_id = best_selling_product['product']
        product = Product.objects.get(id=product_id)
        sales_report_data['best_selling_product'] = {
            'product_name': product.name,
            'quantity_sold': best_selling_product['total_quantity_sold']
        }
    else:
        sales_report_data['best_selling_product'] = None

    return sales_report_data

def sales_report_view(request):
    today = datetime.now().date()
    report_type = request.GET.get('report_type')
    sales_report_data = {}

    if report_type == "today":
        order_items = OrderItem.objects.filter(order__order_date=today, order_status=4)

    elif report_type == "this-week":
        current_week_start = today - timedelta(days=today.weekday())
        current_week_end = current_week_start + timedelta(days=6)
        order_items = OrderItem.objects.filter(order__order_date__range=(current_week_start, current_week_end), order_status=4)

    elif report_type == "this-month":
        current_month_start = today.replace(day=1)
        current_month_end = current_month_start.replace(day=1) + timedelta(days=32)
        current_month_end = current_month_end.replace(day=1) - timedelta(days=1)
        order_items = OrderItem.objects.filter(order__order_date__range=(current_month_start, current_month_end), order_status=4)

    else:
        return JsonResponse({'error': 'Invalid report_type'})

    sales_report_data = calculate_sales_report(order_items)

    data = render_to_string('AdminHome/order_item_list.html', {'order_items' : order_items, 'sales_report_data' : sales_report_data})

    return JsonResponse({'data' : data})


def sales_from_to(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        
        from_date = data.get('from_date')
        to_date = data.get('to_date')

        sales_report_data = {}

        order_items = OrderItem.objects.filter(order__order_date__range=(from_date, to_date),  order_status=4)

        sales_report_data['items_sold'] = len(order_items)

        sales_report_data['revenue'] = 0

        for item in order_items:
            sales_report_data['revenue'] += item.sub_total

        best_selling_product = order_items.values('product').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold').first()

        
        if best_selling_product:
            product_id = best_selling_product['product']
            product = Product.objects.get(id=product_id)

            product_name = product.name
            quantity_sold = best_selling_product['total_quantity_sold']
            sales_report_data['best_selling_product'] = {
                'product_name': product_name,
                'quantity_sold': quantity_sold
            }
        else:
            sales_report_data['best_selling_product'] = None

    data = render_to_string('AdminHome/order_item_list.html', {'order_items' : order_items, 'sales_report_data' : sales_report_data})

    return JsonResponse({'data' : data})

def print_sales_report(request):
    sales_report_html = request.POST.get('sales_report_html', '')
    return render(request, 'AdminHome/sales_report.html', {'sales_report_html': sales_report_html})


from openpyxl import Workbook
from openpyxl.styles import Font
from django.http import HttpResponse
from bs4 import BeautifulSoup
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_excel(request):
    if request.method == 'POST':
        table_data = request.POST.get('table_data')

        soup = BeautifulSoup(table_data, 'html.parser')

        # Create a new workbook and add a worksheet
        wb = Workbook()
        ws = wb.active

        # Function to set header styles
        def set_header_styles(cell):
            cell.font = cell.font.copy(bold=True)

        # Extract table headers and place them in the first row of the worksheet
        headers = [th.text.strip() for th in soup.find_all('th')]
        ws.append(headers)
        for cell in ws[1]:
            set_header_styles(cell)

        # Extract table rows and place them in subsequent rows of the worksheet
        rows = soup.find_all('tr')[1:]  # Exclude header row
        for row in rows:
            row_data = [td.text.strip() for td in row.find_all('td')]
            ws.append(row_data)

        # Save the workbook to a BytesIO object
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        # Set the appropriate content type and headers for file download
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=my_excel_file.xlsx'

        return response
    else:
        return HttpResponse('Invalid request method')
    

from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from bs4 import BeautifulSoup

@csrf_exempt
def generate_pdf(request):
    if request.method == 'POST':
        # Get table data from POST request
        table_data = request.POST.get('table_data')

        # Parse HTML table data using BeautifulSoup
        soup = BeautifulSoup(table_data, 'html.parser')
        headers = [th.text.strip() for th in soup.find('thead').find_all('th')]
        rows = []
        for tr in soup.find('tbody').find_all('tr'):
            row = [td.text.strip() for td in tr.find_all('td')]
            rows.append(row)

        # Calculate total revenue and items sold
        total_revenue = sum(float(row[-1]) for row in rows)
        items_sold = sum(int(row[-2]) for row in rows)

        # Extract best-selling product information if available
        best_selling_product = None
        if rows:
            best_selling_product_row = max(rows, key=lambda row: int(row[-2]))
            best_selling_product = {
                'product_name': best_selling_product_row[1],
                'quantity_sold': int(best_selling_product_row[-2])
            }

        # Create PDF buffer
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Format table data
        table_data_formatted = [headers] + rows
        table = Table(table_data_formatted)

        # Define table style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#a1e6ff'),
            ('TEXTCOLOR', (0, 1), (-1, -1), 'black'),
            ('BACKGROUND', (0, 1), (-1, -1), 'white'),
            ('TEXTCOLOR', (0, 1), (-1, -1), 'black'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), 'white'),
            ('GRID', (0, 0), (-1, -1), 1, 'black')
        ])

        # Apply table style
        table.setStyle(style)

        # Build PDF document with table
        doc.build([table])

        # Move buffer cursor to the beginning
        buffer.seek(0)

        # Create HTTP response with PDF content
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=my_pdf_file.pdf'

        # Return HTTP response
        return response
    else:
        return HttpResponse('Invalid request method')














































































# ---Class Based views---

# class BaseCRUDView(View):
#     model = None
#     form_class = None
#     template_folder = None
#     add_template = None
#     edit_template = None
#     list_template = None
#     success_url = None

#     def get(self, request, obj_id=None):
#         if obj_id:
#             obj = get_object_or_404(self.model, pk=obj_id)
#             form = self.form_class(instance=obj)
#             template = f'{self.template_folder}/{self.edit_template}'
#             return render(request, template, {'form' : form})
#         else:
#             form = self.form_class()
#             template = f'{self.template_folder}/{self.add_template}'
#             objects = self.model.objects.all()
#             return render(request, template, {'form' : form, 'objects' : objects})
        
#     def post(self, request, obj_id=None):
#         if obj_id:
#             obj = get_object_or_404(self.model, pk=obj_id)
#             form = self.form_class(request.POST, request.FILES, instance=obj)
#             template = f'{self.template_folder}/{self.edit_template}'
#         else:
#             form = self.form_class(request.POST, request.FILES)
#             template = f'{self.template_folder}/{self.add_template}'

#         if form.is_valid():
#             form.save()
#             return redirect(self.success_url)
#         return render(request, template, {'form' : form})
    
#     def delete(self, request, obj_id=None):
#         obj = get_object_or_404(self.model, pk=obj_id)
#         obj.delete()
#         return redirect(self.success_url)
    
# class CategoryView(BaseCRUDView):
#     model = Category
#     form_class = CategoryForm
#     template_folder = 'AdminHome'
#     add_template = 'add_category.html'
#     edit_template = 'edit_category.html'
#     list_template = 'category.html'
#     success_url = 'AdminHome:category'

# class BrandView(BaseCRUDView):
#     model = Brand
#     form_class = BrandForm
#     template_folder = 'AdminHome'
#     add_template = 'add_brand.html'
#     edit_template = 'edit_brand.html'
#     list_template = 'brand.html'
#     success_url = 'AdminHome:brand'
    
