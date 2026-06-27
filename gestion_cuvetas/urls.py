from django.urls import path
from .views import *

urlpatterns = [

    ####--------Control Cuvetas--------####
    path("listar_cuvetas", ListaCuvetas.as_view(), name='listar_cuvetas'),
    path("registrar_cuveta", CrearCuveta.as_view(), name='registrar_cuveta'),
    path("actualizar_cuveta/<int:pk>/", ActualizarCuveta.as_view(), name='actualizar_cuveta'),
    path("eliminar_cuveta/<int:pk>/", EliminarCuveta.as_view(), name='eliminar_cuveta'),
    path("detalle_cuveta/<int:pk>/", DetalleCuveta.as_view(), name='detalle_cuveta'),

]