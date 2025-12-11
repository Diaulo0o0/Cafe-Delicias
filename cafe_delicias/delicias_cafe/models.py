from django.db import models
from django.contrib.auth.models import User

# 1. MODELO DE PRODUCTO
class Producto(models.Model):
    # Opciones de categoría
    OPCIONES_CATEGORIA = [
        ('caliente', 'Cafés Calientes'),
        ('frio', 'Cafés Helados'),
        ('grano', 'Café en Grano'),
        ('acompanamiento', 'Dulces'),
    ]

    # Nota: Borré el campo 'id' manual. Django lo crea automático y es más seguro.
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=0) # 0 decimales para CLP
    stock = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=20, choices=OPCIONES_CATEGORIA, default='caliente') 
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    descripcion = models.TextField(max_length=500, blank=True, null=True) 

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre'] # Ordenar alfabéticamente en el admin

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


# 2. MODELO DE PEDIDO (LA BOLETA)
class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha'] # El más reciente primero

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"


# 3. DETALLE DEL PEDIDO (PRODUCTOS DENTRO DE LA BOLETA)
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0) # Precio congelado al momento de compra

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"