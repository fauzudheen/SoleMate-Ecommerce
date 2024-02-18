from django.urls import path
from . import views

app_name='AdminHome'
urlpatterns = [
    path('ad-login/', views.login_view, name='login'),
    path('admin-logout/', views.logout_view, name='logout'),
    path('admin-home/', views.home, name='home'),

    path('admin-users/', views.users, name='users'),
    path('admin-user/block/<int:user_id>/', views.block_user, name='block_user'),
    path('admin-user/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('admin-user/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('admin-banner/', views.banner, name='banner'),
    path('admin-banner/add', views.add_banner, name='add_banner'),
    path('admin-banner/edit/<int:banner_id>/', views.edit_banner, name='edit_banner'),
    path('admin-banner/delete/<int:banner_id>/', views.delete_banner, name='delete_banner'),

    path('admin-daily-sales-page/', views.daily_sales_page, name='daily_sales_page'),
    path('admin-weekly-sales-page/', views.weekly_sales_page, name='weekly_sales_page'),
    path('admin-monthly-sales-page/', views.monthly_sales_page, name='monthly_sales_page'),

    path('admin-daily-sales/', views.daily_sales, name='daily_sales'),
    path('admin-weekly-sales/', views.weekly_sales, name='weekly_sales'),
    path('admin-monthly-sales/', views.monthly_sales, name='monthly_sales'),
    path('admin-sales/', views.sales_report_view, name='sales_report_view'),
    path('admin-sales-from-to/', views.sales_from_to, name='sales_from_to'),
    path('admin-sales-report-print/', views.print_sales_report, name='print_sales_report'),
    
    path('admin-sales-report/excel', views.generate_excel, name='generate_excel'),
    path('admin-sales-report/pdf', views.generate_pdf, name='generate_pdf'),

]
