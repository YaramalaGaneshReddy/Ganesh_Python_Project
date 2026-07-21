from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_dashboard, name='dashboard'),
    path('products/', views.staff_product_list, name='product_list'),
    path('products/add/', views.staff_product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.staff_product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.staff_product_delete, name='product_delete'),
    path('products/<int:pk>/stock/', views.staff_quick_stock_update, name='product_stock_update'),
    path('orders/', views.staff_order_list, name='order_list'),
    path('orders/<int:pk>/', views.staff_order_detail, name='order_detail'),
    path('users/', views.staff_user_list, name='user_list'),
    path('users/<int:pk>/toggle-staff/', views.staff_toggle_user, name='toggle_staff'),
]
