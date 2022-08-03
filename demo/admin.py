from django.contrib import admin

from demo.form import OrderForm
from demo.models import User, \
    Product, Category, Order, \
    ProductsInOrder, ProductsInCart


# Register your models here.

class ItemInOrder(admin.TabularInline):
    model = ProductsInOrder


class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_filter = ('status',)
    list_display = ('date', 'user', 'count_product')
    fields = ('status', 'refuse_reason')
    inlines = (ItemInOrder,)


# admin.site.register(User)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order, OrderAdmin)

# admin.site.register(ProductsInOrder)
# admin.site.register(ProductsInCart)
