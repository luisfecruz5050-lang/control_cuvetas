from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from gestion_usuarios.views import Login, Logout

urlpatterns = [

    # Administración
    path('admin/', admin.site.urls),

    # Autenticación
    path('ingresar/', Login.as_view(), name='ingresar'),
    path('salir/', Logout.as_view(), name='logout'),

    # Apps
    path('gestion_usuarios/', include('gestion_usuarios.urls')),
    path('gestion_clientes/', include('gestion_clientes.urls')),
    path('gestion_estadisticas/', include('gestion_estadisticas.urls')),


    # Página inicial → Login de usuarios
    path('', RedirectView.as_view(url=reverse_lazy('ingresar'), permanent=False)),
]

# Archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)