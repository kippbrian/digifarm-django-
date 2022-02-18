from django.contrib import admin
from .models import Product, OrderProduct, Order, Payment, Coupon, Service


class OrderAdmin(admin.ModelAdmin):
    list_dispaly = ['user', 'ordered']


# Register your models here.
admin.site.register(Product)
admin.site.register(OrderProduct)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Service)
