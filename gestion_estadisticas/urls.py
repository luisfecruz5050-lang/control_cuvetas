# estadisticas/urls.py
from django.urls import path
from .views import *

app_name = 'gestion_estadisticas'

urlpatterns = [
    path("dashboard/", DashboardEstadisticasView.as_view(), name="dashboard"),
    path('autocomplete-usuarios/', AutocompleteUsuarios.as_view(), name='autocomplete_usuarios'),
]
