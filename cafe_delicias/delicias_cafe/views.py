from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.db import transaction
from .models import Producto, Carrito, ItemCarrito

# Create your views here.


def index(request):
    productos = Producto.objects.all()
    return render(request,'cafe_cafe/index.html', {"productos": productos})


#login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")  # vuelve al index ya logueado
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect("login")

    return render(request, "cafe_cafe/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'carrito.html', {'carrito': carrito, 'total': total})


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})

    producto_key = str(producto_id)

    if producto_key in carrito:
        # si ya está en el carrito, revisamos stock
        if carrito[producto_key]['cantidad'] < producto.stock:
            carrito[producto_key]['cantidad'] += 1
        else:
            # mensaje de error si intenta agregar más de lo que hay
            messages.error(request, f"No hay más stock disponible de {producto.nombre}.")
    else:
        if producto.stock > 0:
            carrito[producto_key] = {
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': 1,
            }
        else:
            messages.error(request, f"{producto.nombre} está agotado.")

    request.session['carrito'] = carrito
    return redirect('ver_carrito')


def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito

    return redirect('ver_carrito')


def carrito(request):
    carrito = request.session.get("carrito", {})
    total = sum(item["precio"] * item["cantidad"] for item in carrito.values())

    context = {
        "carrito": carrito,
        "total": total,
    }
    return render(request, 'cafe_cafe/carrito.html', context)


def registro_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validaciones básicas
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect("registro")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe")
            return redirect("registro")

        # Crear el usuario
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Inicia sesión automáticamente después de registrarse
        auth_login(request, user)
        return redirect("index")

    return render(request, "cafe_cafe/registro.html")



@transaction.atomic  # asegura que se ejecute todo o nada
def finalizar_compra(request):
    # Validar si el usuario está logueado
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para poder finalizar la compra. ⚠️")
        return redirect("index")  # lo mandamos al carrito pero con mensaje

    carrito = request.session.get("carrito", {})

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("index")

    # Recorre el carrito y actualiza stock
    for producto_id, item in carrito.items():
        producto = Producto.objects.get(id=producto_id)

        if producto.stock < item['cantidad']:
            messages.error(request, f"No hay suficiente stock de {producto.nombre}.")
            return redirect("index")

        # Descontar stock
        producto.stock -= item['cantidad']
        producto.save()

    # Vaciar carrito
    request.session["carrito"] = {}
    messages.success(request, "Compra realizada con éxito ✅")

    return redirect("index")


def nosotros(request):
    return render(request,'cafe_cafe/nosotros.html')

def politicaspriv(request):
    return render(request,'cafe_cafe/politicaspriv.html')

def politicacookies(request):
    return render(request,'cafe_cafe/politicacookies.html')

def nuestrosservicios(request):
    return render(request,'cafe_cafe/nuestrosservicios.html')