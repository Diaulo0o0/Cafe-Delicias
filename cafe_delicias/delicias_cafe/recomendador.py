from .models import Producto, Pedido, DetallePedido
import random

def recomendar_productos(usuario, cantidad=3):
    # 1. Buscamos el último pedido de este usuario
    ultimo_pedido = Pedido.objects.filter(usuario=usuario).order_by('-fecha').first()

    # Si el usuario nunca ha comprado nada, mostramos productos al azar
    if not ultimo_pedido:
        productos = list(Producto.objects.all())
        if len(productos) > cantidad:
            return random.sample(productos, cantidad)
        return productos

    # 2. Buscamos qué productos compró en ese último pedido
    detalles = DetallePedido.objects.filter(pedido=ultimo_pedido)

    if not detalles.exists():
        return Producto.objects.order_by('?')[:cantidad]

    # 3. Tomamos el primer producto de esa compra para ver su categoría
    # (Asumimos que le interesa esa categoría)
    ultimo_producto_comprado = detalles.first().producto
    categoria_favorita = ultimo_producto_comprado.categoria

    # 4. Buscamos otros productos de la misma categoría
    recomendaciones = Producto.objects.filter(
        categoria=categoria_favorita
    ).exclude(id=ultimo_producto_comprado.id)[:cantidad] # Excluimos el que ya compró

    # 5. Si no hay suficientes recomendaciones en esa categoría, rellenamos con azar
    if not recomendaciones.exists():
        return Producto.objects.order_by('?')[:cantidad]

    return recomendaciones