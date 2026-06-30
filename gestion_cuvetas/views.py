from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from braces.views import PermissionRequiredMixin, MultiplePermissionsRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from .models import ControlCuvetas
from .forms import ControlCuvetasForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
# Al inicio de views.py — agrega esto si no está
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from gestion_clientes.models import Clientes


####--------Vistas autocompletado--------####

class AutocompleteClientes(LoginRequiredMixin, MultiplePermissionsRequiredMixin, View):
    """
    Endpoint AJAX para el select2 del campo 'cliente' en el formulario de cuvetas.
    Devuelve resultados paginados en vez de cargar los 8000+ clientes de una vez.
    """
    permissions = {
        "any": (
            'gestion_cuvetas.registrar_cuveta',
            'gestion_cuvetas.actualizar_cuveta',
        )
    }

    def get(self, request):
        term = request.GET.get('term', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = 20

        qs = Clientes.objects.all()

        if term:
            qs = qs.filter(
                Q(nombre__icontains=term) |
                Q(apellido__icontains=term)
                # Si tu modelo Clientes tiene documento/cédula/teléfono, agrégalo aquí:
                # | Q(documento__icontains=term)
            )

        qs = qs.order_by('nombre', 'apellido')

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size

        results = [
            {'id': c.pk, 'text': f'{c.nombre} {c.apellido}'}
            for c in qs[start:end]
        ]

        return JsonResponse({
            'results': results,
            'pagination': {'more': end < total},
        })


####--------Vistas Control Cuvetas--------####

class ListaCuvetas(LoginRequiredMixin, MultiplePermissionsRequiredMixin, ListView):
    model = ControlCuvetas
    template_name = 'gestion_cuvetas/listar_cuvetas.html'
    context_object_name = 'cuvetas'
    paginate_by = 10
    ordering = ['-id']
    permissions = {
        "any": (
            'gestion_cuvetas.listar_cuvetas',
            'gestion_cuvetas.registrar_cuveta',
            'gestion_cuvetas.actualizar_cuveta',
            'gestion_cuvetas.eliminar_cuveta',
            'gestion_cuvetas.detalle_cuveta',
        )
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        filtro_cliente = self.request.GET.get('cliente', '').strip()
        filtro_estado  = self.request.GET.get('estado', '').strip()
        filtro_fecha   = self.request.GET.get('fecha_registro', '').strip()
        filtro_usuario = self.request.GET.get('usuario', '').strip()

        if filtro_cliente:
            queryset = queryset.filter(
                cliente__nombre__istartswith=filtro_cliente
            ) | queryset.filter(
                cliente__apellido__istartswith=filtro_cliente
            )
        if filtro_estado:
            queryset = queryset.filter(estado=filtro_estado)
        if filtro_fecha:
            queryset = queryset.filter(fecha_registro=filtro_fecha)
        if filtro_usuario:
            queryset = queryset.filter(
                usuario__username__istartswith=filtro_usuario
            )

        return queryset.select_related('cliente', 'usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_cliente']        = self.request.GET.get('cliente', '')
        context['filtro_estado']         = self.request.GET.get('estado', '')
        context['filtro_fecha_registro'] = self.request.GET.get('fecha_registro', '')
        context['filtro_usuario']        = self.request.GET.get('usuario', '')
        context['estado_choices']        = ControlCuvetas.ESTADO_CHOICES

        querystring = self.request.GET.copy()
        if 'page' in querystring:
            querystring.pop('page')
        context['querystring'] = '&' + querystring.urlencode() if querystring else ''
        return context


class DetalleCuveta(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ControlCuvetas
    template_name = 'gestion_cuvetas/detalle_cuveta.html'
    context_object_name = 'cuveta'
    permission_required = 'gestion_cuvetas.detalle_cuveta'

    def get_queryset(self):
        return super().get_queryset().select_related('cliente', 'usuario')


class CrearCuveta(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = ControlCuvetas
    form_class = ControlCuvetasForm
    template_name = 'gestion_cuvetas/registrar_cuveta.html'
    permission_required = 'gestion_cuvetas.registrar_cuveta'
    success_url = reverse_lazy('listar_cuvetas')
    success_message = "El registro de cuvetas fue creado exitosamente"

    def _clean_all_messages(self, request):
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        storage.used = True

    def add_error_messages(self, request, form=None, general_message=None):
        self._clean_all_messages(request)
        if general_message:
            messages.error(request, general_message)
            return
        if form and hasattr(form, 'errors'):
            for field, errors in form.errors.items():
                if errors:
                    messages.error(request, f"Error en {field}: {errors[0]}")
                    return

    def add_success_message(self, request, message):
        self._clean_all_messages(request)
        messages.success(request, message)

    def form_valid(self, form):
        # ← Aquí se asigna el usuario logueado automáticamente
        form.instance.usuario = self.request.user
        self._clean_all_messages(self.request)
        response = super().form_valid(form)
        if self.object.pk:
            self.add_success_message(self.request, "Registro de cuvetas creado correctamente.")
        return response

    def form_invalid(self, form):
        self.add_error_messages(
            request=self.request,
            form=form,
            general_message="No se pudo registrar. Por favor, revise los datos."
        )
        return super().form_invalid(form)


class ActualizarCuveta(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ControlCuvetas
    form_class = ControlCuvetasForm
    template_name = 'gestion_cuvetas/registrar_cuveta.html'
    permission_required = 'gestion_cuvetas.actualizar_cuveta'
    success_url = reverse_lazy('listar_cuvetas')
    success_message = "El registro de cuvetas fue actualizado exitosamente"

    def _clean_all_messages(self, request):
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        storage.used = True

    def add_error_messages(self, request, form=None, general_message=None):
        self._clean_all_messages(request)
        if general_message:
            messages.error(request, general_message)
            return
        if form and hasattr(form, 'errors'):
            for field, errors in form.errors.items():
                if errors:
                    messages.error(request, f"Error en {field}: {errors[0]}")
                    return

    def add_success_message(self, request, message):
        self._clean_all_messages(request)
        messages.success(request, message)

    def form_valid(self, form):
        self._clean_all_messages(self.request)
        response = super().form_valid(form)
        if self.object.pk:
            self.add_success_message(self.request, "Registro de cuvetas actualizado correctamente.")
        return response

    def form_invalid(self, form):
        self.add_error_messages(
            request=self.request,
            form=form,
            general_message="No se pudo actualizar. Por favor, revise los datos."
        )
        return super().form_invalid(form)


class EliminarCuveta(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ControlCuvetas
    template_name = 'gestion_cuvetas/eliminar_cuveta.html'
    permission_required = 'gestion_cuvetas.eliminar_cuveta'
    context_object_name = 'cuveta'
    success_url = reverse_lazy('listar_cuvetas')

    def form_valid(self, form):
        try:
            cliente = self.object.cliente
            result = super().form_valid(form)
            messages.success(
                self.request,
                f"El registro de cuvetas del cliente {cliente} fue eliminado exitosamente."
            )
            return result
        except ProtectedError:
            messages.error(
                self.request,
                f"No se pudo eliminar el registro. Tiene datos asociados que lo protegen."
            )
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error inesperado al eliminar el registro: {str(e)}")
            return HttpResponseRedirect(self.success_url)


class CambiarEstadoCuveta(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'gestion_cuvetas.actualizar_cuveta'

    ESTADOS_PERMITIDOS = ('EN', 'PA', 'DE', 'PE')

    def post(self, request, pk):
        cuveta = get_object_or_404(ControlCuvetas, pk=pk)
        nuevo_estado = request.POST.get('estado')

        if nuevo_estado not in self.ESTADOS_PERMITIDOS:
            messages.error(request, 'Estado no válido.')
            return redirect('listar_cuvetas')

        cuveta.estado = nuevo_estado
        cuveta.save(update_fields=['estado', 'fecha_actualizacion'])
        messages.success(
            request,
            f"El estado del registro de {cuveta.cliente.nombre} {cuveta.cliente.apellido} fue actualizado correctamente."
        )
        return redirect('listar_cuvetas')