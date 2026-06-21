# estadisticas/urls.py
from django.urls import path
from .views import DashboardEstadisticasView

app_name = 'gestion_estadisticas'

urlpatterns = [
    path("dashboard/", DashboardEstadisticasView.as_view(), name="dashboard"),
]
