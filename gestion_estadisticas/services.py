# gestion_estadisticas/services.py

from datetime import date
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django.contrib.auth import get_user_model
from gestion_clientes.models import Clientes
from gestion_cuvetas.models import *

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────

def _base_qs(usuario=None):
    """QuerySet base de ControlCuvetas, filtrado por usuario si se indica.
    Incluye todos los registros, sin importar su estado.
    """
    qs = ControlCuvetas.objects.all()
    if usuario is not None:
        qs = qs.filter(usuario=usuario)
    return qs


# ─────────────────────────────────────────────────────────────
# KPIs globales / por usuario
# ─────────────────────────────────────────────────────────────

def kpis_cuvetas(usuario=None):
    qs = _base_qs(usuario)
    agg = qs.aggregate(
        total_grandes=Sum('cuvetas_grandes'),
        total_pequenas=Sum('cuvetas_pequenas'),
        total_registros=Count('id'),
        clientes_unicos=Count('cliente', distinct=True),
    )
    return {
        'total_grandes':   agg['total_grandes']   or 0,
        'total_pequenas':  agg['total_pequenas']  or 0,
        'total_cuvetas':   (agg['total_grandes'] or 0) + (agg['total_pequenas'] or 0),
        'total_registros': agg['total_registros'] or 0,
        'clientes_unicos': agg['clientes_unicos'] or 0,
    }


# ─────────────────────────────────────────────────────────────
# KPIs mes actual
# ─────────────────────────────────────────────────────────────

def kpis_mes_actual(usuario=None):
    hoy = date.today()
    ini = hoy.replace(day=1)
    qs  = _base_qs(usuario).filter(fecha_registro__gte=ini)
    agg = qs.aggregate(
        grandes=Sum('cuvetas_grandes'),
        pequenas=Sum('cuvetas_pequenas'),
        registros=Count('id'),
        clientes=Count('cliente', distinct=True),
    )
    return {
        'grandes':   agg['grandes']   or 0,
        'pequenas':  agg['pequenas']  or 0,
        'registros': agg['registros'] or 0,
        'clientes':  agg['clientes']  or 0,
    }


# ─────────────────────────────────────────────────────────────
# Distribución por estado
# ─────────────────────────────────────────────────────────────

def distribucion_estados(usuario=None):
    qs = _base_qs(usuario)
    rows = (
        qs.values('estado')
          .annotate(total=Count('id'))
          .order_by('estado')
    )
    etiquetas_map = dict(ControlCuvetas.ESTADO_CHOICES)
    labels  = [etiquetas_map.get(r['estado'], r['estado']) for r in rows]
    valores = [r['total'] for r in rows]
    return labels, valores


# ─────────────────────────────────────────────────────────────
# Cuvetas entregadas por mes (grandes vs pequeñas)
# ─────────────────────────────────────────────────────────────

def cuvetas_por_mes(usuario=None):
    qs = (
        _base_qs(usuario)
        .annotate(mes=TruncMonth('fecha_registro'))
        .values('mes')
        .annotate(
            grandes=Sum('cuvetas_grandes'),
            pequenas=Sum('cuvetas_pequenas'),
        )
        .order_by('mes')
    )
    labels   = [r['mes'].strftime('%b %Y') for r in qs]
    grandes  = [r['grandes']  or 0 for r in qs]
    pequenas = [r['pequenas'] or 0 for r in qs]
    return labels, grandes, pequenas


# ─────────────────────────────────────────────────────────────
# Top 10 clientes con más cuvetas
# ─────────────────────────────────────────────────────────────

def top_clientes(usuario=None, limit=10):
    qs = (
        _base_qs(usuario)
        .values('cliente__nombre', 'cliente__apellido', 'cliente__identificacion')
        .annotate(
            total_grandes=Sum('cuvetas_grandes'),
            total_pequenas=Sum('cuvetas_pequenas'),
            total=Sum('cuvetas_grandes') + Sum('cuvetas_pequenas'),
        )
        .order_by('-total')[:limit]
    )
    return list(qs)


# ─────────────────────────────────────────────────────────────
# Actividad por semana (últimas 8 semanas)
# ─────────────────────────────────────────────────────────────

def actividad_semanal(usuario=None):
    from datetime import timedelta
    hace_8_semanas = date.today() - timedelta(weeks=8)
    qs = (
        _base_qs(usuario)
        .filter(fecha_registro__gte=hace_8_semanas)
        .annotate(semana=TruncWeek('fecha_registro'))
        .values('semana')
        .annotate(registros=Count('id'))
        .order_by('semana')
    )
    labels   = [r['semana'].strftime('Sem %d/%m') for r in qs]
    valores  = [r['registros'] for r in qs]
    return labels, valores


# ─────────────────────────────────────────────────────────────
# Lista de usuarios (para el filtro del dashboard)
# ─────────────────────────────────────────────────────────────

def lista_usuarios():
    """Devuelve usuarios que tienen al menos 1 registro de cuveta."""
    return (
        User.objects
        .filter(controlcuvetas__isnull=False)
        .distinct()
        .values('id', 'username', 'first_name', 'last_name')
    )