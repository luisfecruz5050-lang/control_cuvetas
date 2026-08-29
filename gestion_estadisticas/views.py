# gestion_estadisticas/views.py
import json
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from . import services
from django.http import JsonResponse
from django.db.models import Q
User = get_user_model()


class AutocompleteUsuarios(LoginRequiredMixin, View):
    """
    Endpoint AJAX para el select2 del filtro de usuario en el dashboard.
    Solo accesible por usuarios con rol Administrador.
    """

    def get(self, request):
        # Seguridad: solo admins pueden buscar usuarios
        if not request.user.groups.filter(name="Administrador").exists():
            return JsonResponse({'results': [], 'pagination': {'more': False}})

        term = request.GET.get('term', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = 20

        qs = User.objects.all()

        if term:
            qs = qs.filter(
                Q(first_name__icontains=term) |
                Q(last_name__icontains=term) |
                Q(username__icontains=term) |
                Q(identificacion__icontains=term)
            )

        qs = qs.order_by('first_name', 'last_name', 'username')

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size

        results = [
            {
                'id': u.pk,
                'text': f'{u.first_name} {u.last_name}'.strip() or u.username
            }
            for u in qs[start:end]
        ]

        return JsonResponse({
            'results': results,
            'pagination': {'more': end < total},
        })


class DashboardEstadisticasView(LoginRequiredMixin, TemplateView):
    template_name = "gestion_estadisticas/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_actual = self.request.user
        usuario_id  = self.request.GET.get('usuario_id')

        # ── Rol admin basado en el grupo "Administrador" ──────────────
        es_admin = user_actual.groups.filter(name="Administrador").exists()

        # ── Filtro de usuario ──────────────────────────────────────────
        if es_admin:
            if usuario_id:
                try:
                    usuario_filtro = User.objects.get(pk=usuario_id)
                except User.DoesNotExist:
                    usuario_filtro = None
            else:
                usuario_filtro = None
        else:
            usuario_filtro = user_actual

        # ── Obtener datos de services ───────────────────────────────
        kpis         = services.kpis_cuvetas(usuario_filtro)
        kpis_mes     = services.kpis_mes_actual(usuario_filtro)
        top          = services.top_clientes(usuario_filtro)
        usuarios     = services.lista_usuarios()

        mes_labels, mes_grandes, mes_pequenas = services.cuvetas_por_mes(usuario_filtro)
        estado_labels, estado_vals            = services.distribucion_estados(usuario_filtro)
        sem_labels, sem_vals                  = services.actividad_semanal(usuario_filtro)

        # ── Nombre para el encabezado ───────────────────────────────
        if usuario_filtro:
            nombre_vista = (
                f"{usuario_filtro.first_name} {usuario_filtro.last_name}".strip()
                or usuario_filtro.username
            )
        else:
            nombre_vista = "Todos los usuarios"

        # ── CONSTRUIR CONTEXTO COMPLETO ─────────────────────────────
        context.update({
            "usuarios":          [],
            "usuario_id_sel":    int(usuario_id) if usuario_id else None,
            "usuario_sel_obj":   usuario_filtro,
            "nombre_vista":      nombre_vista,
            "es_admin":          es_admin,

            "total_grandes":     kpis["total_grandes"],
            "total_pequenas":    kpis["total_pequenas"],
            "total_cuvetas":     kpis["total_cuvetas"],
            "total_registros":   kpis["total_registros"],
            "clientes_unicos":   kpis["clientes_unicos"],

            "mes_grandes":       kpis_mes["grandes"],
            "mes_pequenas":      kpis_mes["pequenas"],
            "mes_registros":     kpis_mes["registros"],
            "mes_clientes":      kpis_mes["clientes"],

            "mes_labels":        json.dumps(mes_labels),
            "mes_data_grandes":  json.dumps(mes_grandes),
            "mes_data_pequenas": json.dumps(mes_pequenas),
            "estado_labels":     json.dumps(estado_labels),
            "estado_vals":       json.dumps(estado_vals),
            "sem_labels":        json.dumps(sem_labels),
            "sem_vals":          json.dumps(sem_vals),

            "top_clientes":      top,

            "total_ventas":      0,
            "ticket_promedio":   0,
            "total_clientes":    0,
            "total_usuarios":    0,
            "total_facturas":    0,
            "ventas_mes":        0,
            "facturas_mes":      0,
            "clientes_mes":      0,
            "usuarios_mes":      0,
            "variaciones": {
                "ventas": {"pct": None, "up": True},
                "ticket": {"pct": None, "up": True},
                "clientes": {"pct": None, "up": True},
            },
            "ventas_labels":     json.dumps([]),
            "ventas_subtotales": json.dumps([]),
            "ventas_cantidades": json.dumps([]),
            "clientes_labels":   json.dumps([]),
            "clientes_totales":  json.dumps([]),
            "usuarios_labels":   json.dumps([]),
            "usuarios_totales":  json.dumps([]),
            "operaciones_recientes": [],
        })

        return context
