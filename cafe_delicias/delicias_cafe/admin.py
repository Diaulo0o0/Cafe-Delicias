from django.contrib import admin
from .models import Producto, Pedido, DetallePedido

# 1. Configuración del Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'imagen')
    list_editable = ('precio', 'stock')
    search_fields = ('nombre',)
    list_filter = ('categoria',)
    list_per_page = 10

# 2. Configuración para ver el Detalle dentro del Pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    can_delete = False

# 3. Configuración del Pedido (Boleta)
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'total')
    list_filter = ('fecha',)
    search_fields = ('usuario__username', 'id')
    inlines = [DetallePedidoInline]
    readonly_fields = ('fecha', 'total')

# 4. Personalización del Panel
admin.site.site_header = "Administración Café Delicias"
admin.site.site_title = "Café Delicias Admin"
admin.site.index_title = "Panel de Control"