from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Purchase URLs
    path('purchases/new/<int:customer_id>/', views.purchase_create, name='purchase_create'),
    path('customers/<int:pk>/detail/', views.customer_detail, name='customer_detail'),
    path('purchases/<int:pk>/delete/', views.purchase_delete, name='purchase_delete'),

    # Dashboard URL
    path('dashboard/', views.dashboard, name='dashboard'),
]
