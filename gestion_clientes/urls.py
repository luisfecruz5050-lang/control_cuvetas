from django.urls import path
from .views import *

urlpatterns = [
    ####--------Clientes--------####
    path("listar_clientes", ListaClientes.as_view(), name='listar_clientes'),
    path("registrar_cliente", CrearCliente.as_view(), name='registrar_cliente'),
    path("actualizar_cliente/<int:pk>/", ActualizarCliente.as_view(), name='actualizar_cliente'),
    path("eliminar_cliente/<int:pk>/", EliminarCliente.as_view(), name='eliminar_cliente'),   
    path("detalle_cliente/<int:pk>/", DetalleCliente.as_view(), name='detalle_cliente'),
    path('cargar-excel/',     CargueClientesExcel.as_view(),        name='cargar_clientes_excel'),
    path('descargar-plantilla/', DescargarPlantillaClientes.as_view(), name='descargar_plantilla_clientes'),
]