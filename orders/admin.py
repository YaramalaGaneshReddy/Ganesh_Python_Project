from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'address', 'city')
    inlines = [OrderItemInline]
