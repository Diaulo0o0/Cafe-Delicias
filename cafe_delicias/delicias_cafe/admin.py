from django.contrib import admin
from .models import Producto, Carrito, ItemCarrito

# Register your models here.

admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)