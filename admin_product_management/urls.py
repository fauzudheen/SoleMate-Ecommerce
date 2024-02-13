from django.urls import path
from . import views

app_name='admin_product_management'
urlpatterns = [

    path('admin-category/', views.category, name='category'),
    path('admin-category/add', views.add_category, name='add_category'),
    path('admin-category/unlisted', views.unlisted_categories, name='unlisted_categories'),
    path('admin-category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('admin-category/list/<int:category_id>/', views.list_category, name='list_category'),    
    path('admin-category/unlist/<int:category_id>/', views.unlist_category, name='unlist_category'),

    path('admin-brand/', views.brand, name='brand'),
    path('admin-brand/add', views.add_brand, name='add_brand'),
    path('admin-brand/edit/<int:brand_id>/', views.edit_brand, name='edit_brand'),
    path('admin-brand/unlisted', views.unlisted_brands, name='unlisted_brands'),    
    path('admin-brand/list/<int:brand_id>/', views.list_brand, name='list_brand'),    
    path('admin-brand/unlist/<int:brand_id>/', views.unlist_brand, name='unlist_brand'),    

    path('admin-product/', views.product, name='product'),
    path('admin-product/add', views.add_product, name='add_product'),
    path('admin-product/view/<int:product_id>/', views.view_product, name='view_product'),
    path('admin-product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admin-product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin-product/deleted/', views.deleted_product, name='deleted_product'),
    path('admin-product/restore/<int:product_id>/', views.restore_product, name='restore_product'),

    path('admin-product/image/delete/<int:image_id>/', views.delete_image, name='delete_image'),

    path('admin-product_variant/add/<int:product_id>/', views.add_product_variant, name='add_product_variant'),
    path('admin-product_variant/edit/<int:product_variant_id>/', views.edit_product_variant, name='edit_product_variant'),
    path('admin-product_variant/delete/<int:product_variant_id>/', views.delete_product_variant, name='delete_product_variant'),

    path('admin-offer/add/<int:product_id>/', views.add_offer, name='add_offer'),
    path('admin-offer/edit/<int:offer_id>/', views.edit_offer, name='edit_offer'),
    path('admin-offer/delete/<int:offer_id>/', views.delete_offer, name='delete_offer'),
    
    path('admin-coupon/', views.coupon, name='coupon'),
    path('admin-coupon/add', views.add_coupon, name='add_coupon'),
    path('admin-coupon/edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('admin-coupon/activate/<int:coupon_id>/', views.activate_coupon, name='activate_coupon'),
    path('admin-coupon/deactivate/<int:coupon_id>/', views.deactivate_coupon, name='deactivate_coupon'),
    path('admin-coupon/deactivated', views.deactivated_coupons, name='deactivated_coupons'),
    
]

