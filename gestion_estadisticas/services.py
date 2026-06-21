from decimal import Decimal
from datetime import date

from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model

from gestion_clientes.models import Clientes

User = get_user_model()


# ============================================================
# CLIENTES POR MES
# ============================================================
def clientes_por_mes():
    qs = (
        Clientes.objects
        .annotate(mes=TruncMonth("fecha_registro"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )
    labels  = [row["mes"].strftime("%Y-%m") for row in qs]
    totales = [row["total"] for row in qs]
    return labels, totales


# ============================================================
# USUARIOS POR MES  (date_joined de AbstractUser)
# ============================================================
def usuarios_por_mes():
    qs = (
        User.objects
        .annotate(mes=TruncMonth("date_joined"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )
    labels  = [row["mes"].strftime("%Y-%m") for row in qs]
    totales = [row["total"] for row in qs]
    return labels, totales


# ============================================================
# CONTEOS GLOBALES  (KPI cards)
# ============================================================
def conteos_globales():
    return {
        "total_clientes" : Clientes.objects.count(),
        "total_usuarios" : User.objects.count(),
    }


# ============================================================
# CONTEOS MES ACTUAL
# ============================================================
def conteos_mes_actual():
    hoy     = date.today()
    ini_mes = hoy.replace(day=1)
    return {
        "clientes_mes": Clientes.objects.filter(fecha_registro__date__gte=ini_mes).count(),
        "usuarios_mes": User.objects.filter(date_joined__date__gte=ini_mes).count(),
    }


