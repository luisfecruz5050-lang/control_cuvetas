from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from braces.views import PermissionRequiredMixin, MultiplePermissionsRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Clientes
from .forms import ClientesForm
from django.db.models.deletion import ProtectedError
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


####--------Vistas del curso--------####
class ListaClientes(LoginRequiredMixin, MultiplePermissionsRequiredMixin, ListView):
    """
    Clase para listar los clientes registrados en el sistema.
    """
    model = Clientes
    template_name = 'gestion_clientes/listar_clientes.html'
    context_object_name = 'clientes'
    paginate_by = 10
    ordering = ['-fecha_registro']
    permissions = {
        "any": (
            'gestion_clientes.listar_clientes',
            'gestion_clientes.registrar_cliente',
            'gestion_clientes.actualizar_cliente',
            'gestion_clientes.eliminar_cliente',
            'gestion_clientes.detalle_cliente'
        )
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        # 🔹 Obtener filtros desde la URL
        filtro_nombre = self.request.GET.get('nombre', '').strip()
        filtro_apellido = self.request.GET.get('apellido', '').strip()
        filtro_identificacion = self.request.GET.get('identificacion', '').strip()
        filtro_telefono = self.request.GET.get('telefono', '').strip()
        filtro_email = self.request.GET.get('email', '').strip()
        filtro_genero = self.request.GET.get('genero', '').strip()

        # 🔍 Filtro por nombre
        if filtro_nombre:
            queryset = queryset.filter(nombre__istartswith=filtro_nombre)

        # 🔍 Filtro por apellido
        if filtro_apellido:
            queryset = queryset.filter(apellido__istartswith=filtro_apellido)

        # 🔍 Filtro por identificación (solo numérico)
        if filtro_identificacion:
            if filtro_identificacion.isdigit():
                queryset = queryset.filter(identificacion__istartswith=filtro_identificacion)
            else:
                queryset = queryset.none()

        # 🔍 Filtro por teléfono (solo numérico)
        if filtro_telefono:
            if filtro_telefono.isdigit():
                queryset = queryset.filter(telefono__istartswith=filtro_telefono)
            else:
                queryset = queryset.none()

        # 🔍 Filtro por correo
        if filtro_email:
            queryset = queryset.filter(email__istartswith=filtro_email)

        # 🔍 Filtro por genero
        if filtro_genero:
            queryset = queryset.filter(genero__istartswith=filtro_genero)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Guardar filtros actuales en el contexto
        context['filtro_nombre'] = self.request.GET.get('nombre', '')
        context['filtro_apellido'] = self.request.GET.get('apellido', '')
        context['filtro_identificacion'] = self.request.GET.get('identificacion', '')
        context['filtro_telefono'] = self.request.GET.get('telefono', '')
        context['filtro_email'] = self.request.GET.get('email', '')
        context['filtro_genero'] = self.request.GET.get('genero', '')

        # Mantener los filtros al cambiar de página (sin duplicar 'page')
        querystring = self.request.GET.copy()
        if 'page' in querystring:
            querystring.pop('page')
        context['querystring'] = '&' + querystring.urlencode() if querystring else ''

        return context



class DetalleCliente(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Clientes
    template_name = 'gestion_clientes/detalle_cliente.html'
    permission_required = 'gestion_clientes.detalle_cliente'
    success_url = reverse_lazy('clientes')



class CrearCliente(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Clase que permite la creación de un nuevo objeto en la base de datos.

    :param CreateView: Maneja la creacion de objetos
    :type CreateView: Objeto
    """    
    
    model = Clientes
    form_class = ClientesForm
    template_name = 'gestion_clientes/registrar_cliente.html'
    permission_required = 'gestion_clientes.registrar_cliente'
    success_url = reverse_lazy('listar_clientes')
    success_message = "El Cliente fue registrado exitosamente"
    
    def _clean_all_messages(self, request):
        """
        Limpia TODOS los mensajes existentes de manera efectiva
        """
        storage = messages.get_messages(request)
        for _ in storage:  # Consume todos los mensajes
            pass
        storage.used = True  # Marca todos como leídos

    def add_error_messages(self, request, form=None, general_message=None):
        """Agrega mensajes de error limpiando primero TODOS los existentes"""
        self._clean_all_messages(request)
    
        # Prioridad 1: Mensaje general si existe
        if general_message:
            messages.error(request, general_message)
            return  # Salimos para mostrar solo el mensaje general
    
        # Prioridad 2: Primer error del formulario si existe
        if form and hasattr(form, 'errors'):
            for field, errors in form.errors.items():
                if errors:
                    messages.error(request, f"Error en {field}: {errors[0]}")
                    return  # Mostramos solo el primer error encontrado

    def add_success_message(self, request, message):
        """Agrega mensaje de éxito limpiando primero TODOS los existentes"""
        self._clean_all_messages(request)
        messages.success(request, message)

    def form_invalid(self, form):
        """Maneja formularios inválidos"""
        self.add_error_messages(
            request=self.request,
            form=form,
            general_message="No se pudo registrar el Cliente. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        """Maneja formularios válidos"""
        self._clean_all_messages(self.request)  # Limpieza total garantizada
    
        response = super().form_valid(form)
    
        if self.object.pk:
            self.add_success_message(self.request, "Cliente registrado correctamente.")
    
        return response


class ActualizarCliente(LoginRequiredMixin, PermissionRequiredMixin,SuccessMessageMixin, UpdateView):
    """Clase que permite la ctualización de los datos de un objeto específico.

    :param UpdateView: Manejar actualizaciones de objetos.
    :type UpdateView: Objeto
    """       
    
    model = Clientes
    form_class = ClientesForm
    template_name= 'gestion_clientes/registrar_cliente.html'
    permission_required = 'gestion_clientes.registrar_cliente'
    success_url = reverse_lazy('listar_clientes')
    success_message = "El Cliente fue actualizado exitosamente"
    
    
    def _clean_all_messages(self, request):
        """
        Limpia TODOS los mensajes existentes de manera efectiva
        """
        storage = messages.get_messages(request)
        for _ in storage:  # Consume todos los mensajes
            pass
        storage.used = True  # Marca todos como leídos

    def add_error_messages(self, request, form=None, general_message=None):
        """Agrega mensajes de error limpiando primero TODOS los existentes"""
        self._clean_all_messages(request)
    
        # Prioridad 1: Mensaje general si existe
        if general_message:
            messages.error(request, general_message)
            return  # Salimos para mostrar solo el mensaje general
    
        # Prioridad 2: Primer error del formulario si existe
        if form and hasattr(form, 'errors'):
            for field, errors in form.errors.items():
                if errors:
                    messages.error(request, f"Error en {field}: {errors[0]}")
                    return  # Mostramos solo el primer error encontrado

    def add_success_message(self, request, message):
        """Agrega mensaje de éxito limpiando primero TODOS los existentes"""
        self._clean_all_messages(request)
        messages.success(request, message)

    def form_invalid(self, form):
        """Maneja formularios inválidos"""
        self.add_error_messages(
            request=self.request,
            form=form,
            general_message="No se pudo registrar el Cliente. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        """Maneja formularios válidos"""
        self._clean_all_messages(self.request)  # Limpieza total garantizada
    
        response = super().form_valid(form)
    
        if self.object.pk:
            self.add_success_message(self.request, "Cliente actualizado correctamente.")
    
        return response


class EliminarCliente(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Clientes
    template_name = 'gestion_clientes/eliminar_cliente.html'
    permission_required = 'gestion_clientes.eliminar_cliente'
    success_url = reverse_lazy('listar_clientes')

    def form_valid(self, form):
        try:
            nombre = self.object.nombre  # self.object ya está asignado por el flujo de Django
            result = super().form_valid(form)  # Aquí se hace la eliminación real
            messages.success(self.request, f"El Cliente {nombre} fue eliminado exitosamente")
            return result

        except ProtectedError:
            messages.error(
                self.request,
                f"No se pudo eliminar el Cliente {self.object.nombre}. Tiene facturas asociadas."
            )
            return HttpResponseRedirect(self.success_url)

        except Exception as e:
            messages.error(
                self.request,
                f"Error inesperado al eliminar el Cliente: {str(e)}"
            )
            return HttpResponseRedirect(self.success_url)