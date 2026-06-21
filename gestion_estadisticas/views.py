from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import services


# ============================================================
# Contexto del Dashboard
# ============================================================

def get_dashboard_context():
    clientes_labels, clientes_totales = services.clientes_por_mes()
    usuarios_labels, usuarios_totales = services.usuarios_por_mes()
    conteos                           = services.conteos_globales()
    conteos_mes                       = services.conteos_mes_actual()

    return {

        # ── KPIs globales (tarjetas) ────────────────────────
        "total_clientes"  : conteos["total_clientes"],
        "total_usuarios"  : conteos["total_usuarios"],

        # ── KPIs mes actual ─────────────────────────────────
        "clientes_mes": conteos_mes["clientes_mes"],
        "usuarios_mes": conteos_mes["usuarios_mes"],

        # ── Clientes por mes ────────────────────────────────
        "clientes_labels" : clientes_labels,
        "clientes_totales": clientes_totales,

        # ── Usuarios por mes ────────────────────────────────
        "usuarios_labels" : usuarios_labels,
        "usuarios_totales": usuarios_totales,
    }


# ============================================================
# Vista principal
# ============================================================

class DashboardEstadisticasView(LoginRequiredMixin, TemplateView):
    template_name = "gestion_estadisticas/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_dashboard_context())
        return context