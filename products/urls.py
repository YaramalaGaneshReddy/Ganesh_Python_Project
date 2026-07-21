from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]