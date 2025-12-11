"""cafe_delicias URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), # Página principal de la aplicación, donde se muestran los productos.
    path('carrito/', views.carrito, name='carrito'), # Muestra el carrito de compras.
    path('login/', views.login_view, name='login'), # Página para iniciar sesión en el sitio.  
    path('logout/', views.logout_view, name='logout'), # Cierra la sesión del usuario.
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('nosotros', views.nosotros, name='nosotros'),
    path('politicaspriv', views.politicaspriv, name='politicaspriv'),
    path('politicacookies', views.politicacookies, name='politicacookies'),
    path('nuestrosservicios', views.nuestrosservicios, name='nuestrosservicios'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'), # Agrega un producto al carrito según su ID.
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),# Elimina un producto del carrito según su ID.
    path('registro/', views.registro_view, name='registro'), # Página para que un usuario se registre.
    path('finalizar_compra/', views.finalizar_compra, name='finalizar_compra'), # Finaliza la compra: descuenta stock y muestra mensaje de éxito
    path('boleta/<int:pedido_id>/', views.boleta, name='boleta'),
    path('pago/', views.vista_pago, name='pago'),
    path('ayuda/preguntas/', views.preguntas_frecuentes, name='preguntas'),
    path('ayuda/envios/', views.envios, name='envios'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)