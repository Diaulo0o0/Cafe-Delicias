import unicodedata
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required


from .models import Producto, Pedido, DetallePedido

# --- FUNCIONES AUXILIARES ---

def eliminar_tildes(texto):
    """Normaliza texto para búsquedas (ej: 'Café' -> 'cafe')"""
    if not texto:
        return ""
    texto_normalizado = unicodedata.normalize('NFD', str(texto))
    texto_sin_tildes = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_sin_tildes.lower()

# --- VISTAS PRINCIPALES ---

def index(request):
    # 1. Obtener todos los productos
    productos_filtrados = Producto.objects.all()
    
    # 2. Capturar filtros
    query = request.GET.get('q')
    categoria_filtro = request.GET.get('categoria')
    orden = request.GET.get('orden')
    
    esta_filtrando = False 

    # Filtros de Base de Datos
    if categoria_filtro:
        productos_filtrados = productos_filtrados.filter(categoria=categoria_filtro)
        esta_filtrando = True

    if orden == 'precio_asc':
        productos_filtrados = productos_filtrados.order_by('precio')
        esta_filtrando = True
    elif orden == 'precio_desc':
        productos_filtrados = productos_filtrados.order_by('-precio')
        esta_filtrando = True

    # Búsqueda de texto (Python)
    if query:
        esta_filtrando = True
        query_limpia = eliminar_tildes(query)
        resultados = []
        for producto in productos_filtrados:
            nombre_limpio = eliminar_tildes(producto.nombre)
            if query_limpia in nombre_limpio:
                resultados.append(producto)
        productos_filtrados = resultados

    # Listas para el Home normal (Secciones con títulos)
    cafes_calientes = Producto.objects.filter(categoria='caliente')
    cafes_frios = Producto.objects.filter(categoria='frio')

    
    recomendaciones = None
    if request.user.is_authenticated:
        try:
            from .recomendador import recomendar_productos
            recomendaciones = recomendar_productos(request.user)
        except ImportError:
            recomendaciones = None

    context = {
        "esta_filtrando": esta_filtrando,
        "productos": productos_filtrados,
        "cafes_calientes": cafes_calientes,
        "cafes_frios": cafes_frios,
        "recomendaciones": recomendaciones
    }
    return render(request, 'cafe_cafe/index.html', context)


# --- CARRITO Y COMPRA ---

def carrito(request):
    """Muestra la página del carrito"""
    carrito = request.session.get("carrito", {})
    total = sum(item["precio"] * item["cantidad"] for item in carrito.values())
    total = int(total) # Sin decimales

    context = {
        "carrito": carrito,
        "total": total,
    }
    return render(request, 'cafe_cafe/carrito.html', context)


def ver_carrito(request):
    return carrito(request)


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    producto_key = str(producto_id)

    if producto_key in carrito:
        if carrito[producto_key]['cantidad'] < producto.stock:
            carrito[producto_key]['cantidad'] += 1
            messages.success(request, f"¡{producto.nombre} agregado! (+1)")
        else:
            messages.error(request, f"No hay más stock disponible de {producto.nombre}.")
    else:
        if producto.stock > 0:
            carrito[producto_key] = {
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': 1,
                'imagen': producto.imagen.url if producto.imagen else '',
            }
            messages.success(request, f"¡{producto.nombre} agregado al carrito! 🛒")
        else:
            messages.error(request, f"{producto.nombre} está agotado.")

    request.session['carrito'] = carrito
    return redirect('index')


def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
    return redirect('carrito')


@transaction.atomic
def finalizar_compra(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para finalizar la compra.")
        return redirect("login")

    carrito = request.session.get("carrito", {})
    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("index")

    # 1. Crear el Pedido (Boleta)
    nuevo_pedido = Pedido.objects.create(
        usuario=request.user,
        total=0 
    )

    total_acumulado = Decimal(0)

    # 2. Procesar ítems
    for producto_id, item in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            continue 

        if producto.stock < item['cantidad']:
            messages.error(request, f"Stock insuficiente para {producto.nombre}.")
            nuevo_pedido.delete()
            return redirect("carrito")

        precio_unitario = Decimal(str(item['precio']))
        cantidad = int(item['cantidad'])

        DetallePedido.objects.create(
            pedido=nuevo_pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )

        total_acumulado += precio_unitario * cantidad
        producto.stock -= cantidad
        producto.save()

    # 3. Guardar total y limpiar
    nuevo_pedido.total = total_acumulado
    nuevo_pedido.save()

    request.session["carrito"] = {}
    messages.success(request, "¡Compra exitosa! Aquí tienes tu boleta.")

    return redirect("boleta", pedido_id=nuevo_pedido.id)


def boleta(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'cafe_cafe/boleta.html', {'pedido': pedido})


# --- AUTENTICACIÓN ---

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect("login")
    return render(request, "cafe_cafe/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def registro_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        p1 = request.POST.get("password1")
        p2 = request.POST.get("password2")

        if p1 != p2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect("registro")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
            return redirect("registro")

        user = User.objects.create_user(username=username, email=email, password=p1)
        user.save()
        auth_login(request, user)
        return redirect("index")
    return render(request, "cafe_cafe/registro.html")

def vista_pago(request):
    # 1. Validar si está logueado
    if not request.user.is_authenticated:
        messages.error(request, "Inicia sesión para pagar.")
        return redirect("login")

    # 2. Validar si hay carrito
    carrito = request.session.get("carrito", {})
    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("index")

    # 3. Calcular total para mostrarlo en el botón
    total = sum(item["precio"] * item["cantidad"] for item in carrito.values())
    total = int(total)

    return render(request, 'cafe_cafe/pago.html', {'total': total})


# --- PÁGINAS ESTÁTICAS ---

def nosotros(request):
    return render(request, 'cafe_cafe/nosotros.html')

def politicaspriv(request):
    return render(request, 'cafe_cafe/politicaspriv.html')

def nuestrosservicios(request):
    return render(request, 'cafe_cafe/nuestrosservicios.html')

def politicacookies(request): 
    return render(request, 'cafe_cafe/politicacookies.html')

def preguntas_frecuentes(request):
    return render(request, 'cafe_cafe/preguntas.html')

def envios(request):
    return render(request, 'cafe_cafe/envios.html')