from django.shortcuts import render
from .models import *
from .forms import *
from django.views.generic import FormView, CreateView, UpdateView, ListView, TemplateView, DetailView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from braces.views import PermissionRequiredMixin, MultiplePermissionsRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, login, authenticate
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required 
from django.http import HttpResponseRedirect
from django.db.models.deletion import ProtectedError
from django.db.models import ProtectedError
from django.db import transaction
from .forms import LoginForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group


class Login(FormView):
    form_class = LoginForm
    template_name = 'baseHTML/inicio_prueba.html'
    success_url = reverse_lazy('gestion_estadisticas:dashboard')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inicio')
        return super().get(request, *args, **kwargs)


    def form_valid(self, form):
        username = form.cleaned_data['username'].strip().lower()
        password = form.cleaned_data['password']

        try:
            usuario_obj = Usuario.objects.get(username__iexact=username)
        except Usuario.DoesNotExist:
            usuario_obj = None

        # ── Verificaciones de estado ANTES de autenticar ──────────────
        if usuario_obj:

            if usuario_obj.estado == 'IN':
                messages.error(
                    self.request,
                    "Tu cuenta está inactiva. Contacta al administrador."
                )
                return self.form_invalid(form)

            if usuario_obj.estado == 'BL':
                if usuario_obj.motivo_bloqueo == 'admin':
                    messages.error(
                        self.request,
                        "Tu cuenta ha sido bloqueada por un administrador. "
                        "Contacta al administrador para más información."
                    )
                else:
                    messages.error(
                        self.request,
                        "Tu cuenta ha sido bloqueada por múltiples intentos fallidos. "
                        "Contacta al administrador para recuperar el acceso."
                    )
                return self.form_invalid(form)

        # ── Autenticación ─────────────────────────────────────────────
        user = authenticate(request=self.request, username=username, password=password)

        if user is not None and user.is_active:
            user.resetear_intentos()
            login(self.request, user)
            messages.success(self.request, "Sesión iniciada correctamente.")
            return super().form_valid(form)

        # ── Credenciales inválidas ────────────────────────────────────
        if usuario_obj:
            usuario_obj.registrar_intento_fallido()
            if usuario_obj.estado == 'BL':
                messages.error(
                    self.request,
                    "Has superado el número máximo de intentos. "
                    "Tu cuenta ha sido bloqueada."
                )
            else:
                restantes = Usuario.MAX_INTENTOS - usuario_obj.intentos_fallidos
                messages.error(
                    self.request,
                    f"Usuario o contraseña incorrectos. Te quedan {restantes} intento(s)."
                )
        else:
            messages.error(self.request, "Usuario o contraseña incorrectos.")

        return self.form_invalid(form)


class Logout(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        request.session.flush()

        messages.success(
            request,
            "Sesión cerrada correctamente."
        )

        return redirect('ingresar')
    

######-------Crud del Usuaio-------######
class ListaUsuario(LoginRequiredMixin, MultiplePermissionsRequiredMixin, ListView):
    """Clase para mostrar la lista de usuarios con filtros y paginación."""
    model = Usuario
    template_name = 'gestion_usuarios/listar_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 10
    ordering = ['-id']
    permissions = {
        "any": (
            'gestion_usuarios.listar_usuarios',
            'gestion_usuarios.registrar_usuario',
            'gestion_usuarios.actualizar_usuario',
            'gestion_usuarios.eliminar_usuario',
            'gestion_usuarios.detalle_usuario',
            'gestion_usuarios.usuario_usuario',
        )
    }

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('groups', 'user_permissions')
        filtro_identificacion = self.request.GET.get('identificacion', '').strip()
        filtro_nombre = self.request.GET.get('nombre', '').strip()
        filtro_apellido = self.request.GET.get('apellido', '').strip()
        filtro_correo = self.request.GET.get('correo', '').strip()
        filtro_rol = self.request.GET.get('rol', '').strip()
        filtro_estado  = self.request.GET.get('estado', '').strip()


        # Filtro por identificación (numérico)
        if filtro_identificacion:
            if filtro_identificacion.isdigit():  # Verifica que sea número
                queryset = queryset.filter(identificacion__istartswith=filtro_identificacion)
            else:
                queryset = queryset.none()  # Si no es número, no devuelve nada

        # 🔍 Filtro por nombre
        if filtro_nombre:
            queryset = queryset.filter(first_name__istartswith=filtro_nombre)

        # 🔍 Filtro por apellido
        if filtro_apellido:
            queryset = queryset.filter(last_name__istartswith=filtro_apellido)

        # 🔍 Filtro por correo
        if filtro_correo:
            queryset = queryset.filter(email__istartswith=filtro_correo)

        # 🔍 Filtro por rol
        if filtro_rol:
            queryset = queryset.filter(groups__name__istartswith=filtro_rol).distinct()

        # Filtro extra: por estado (Borrador, Enviada, Aceptada...)
        if filtro_estado:
            queryset = queryset.filter(estado=filtro_estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Guardar filtros actuales
        context['filtro_identificacion'] = self.request.GET.get('identificacion', '')
        context['filtro_nombre'] = self.request.GET.get('nombre', '')
        context['filtro_apellido'] = self.request.GET.get('apellido', '')
        context['filtro_correo'] = self.request.GET.get('correo', '')
        context['filtro_rol'] = self.request.GET.get('rol', '')
        context['estados']        = Usuario.ESTADOS  # Para el select del filtro

        # Mantener filtros en la paginación sin duplicar el parámetro 'page'
        querystring = self.request.GET.copy()
        if 'page' in querystring:
            querystring.pop('page')
        context['querystring'] = '&' + querystring.urlencode() if querystring else ''

        return context



class VistaUsuario(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Clase para mostrar la información detallada de un objeto específico.

    :param DetailView: visualiza los detalles de un objeto.
    :type DetailView: Objeto
    """

    model = Usuario
    template_name = 'gestion_usuarios/detalle_usuario.html'
    permission_required = 'gestion_usuarios.detalle_usuario'
    success_url = reverse_lazy('usuarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()

        # --- Roles (groups) ---
        roles_qs = usuario.groups.all().order_by('name')

        paginator_roles = Paginator(roles_qs, 4)
        page_roles = self.request.GET.get('page_roles', 1)
        try:
            page_obj_roles = paginator_roles.page(page_roles)
        except (PageNotAnInteger, EmptyPage):
            page_obj_roles = paginator_roles.page(1)

        context['roles']              = page_obj_roles
        context['paginator_roles']    = paginator_roles
        context['page_obj_roles']     = page_obj_roles
        context['is_paginated_roles'] = paginator_roles.num_pages > 1

        # --- Permisos adicionales ---
        permisos_qs = usuario.user_permissions.all().order_by('name')

        paginator_permisos = Paginator(permisos_qs, 4)
        page_permisos = self.request.GET.get('page_permisos', 1)
        try:
            page_obj_permisos = paginator_permisos.page(page_permisos)
        except (PageNotAnInteger, EmptyPage):
            page_obj_permisos = paginator_permisos.page(1)

        context['permisos']              = page_obj_permisos
        context['paginator_permisos']    = paginator_permisos
        context['page_obj_permisos']     = page_obj_permisos
        context['is_paginated_permisos'] = paginator_permisos.num_pages > 1

        # querystring sin los parámetros de página
        querystring = self.request.GET.copy()
        for key in ('page_roles', 'page_permisos'):
            if key in querystring:
                querystring.pop(key)
        context['querystring'] = '&' + querystring.urlencode() if querystring else ''

        return context


class UserUsuario(LoginRequiredMixin, PermissionRequiredMixin, View):
    model = Usuario
    template_name = 'gestion_usuarios/usuario_usuario.html'
    permission_required = 'gestion_usuarios.usuario_usuario'
    success_url = reverse_lazy('usuarios')

    def handle_no_permission(self, *args, **kwargs):
        """Evita conflicto entre mixins de braces y Django."""
        return redirect('gestion_empresas:login_empresa')

    def get(self, request, *args, **kwargs):
        """Muestra el perfil del usuario."""
        usuario = request.user

        # --- Roles (groups) ---
        roles_qs = usuario.groups.all().order_by('name')

        paginator_roles = Paginator(roles_qs, 4)
        page_roles = request.GET.get('page_roles', 1)
        try:
            page_obj_roles = paginator_roles.page(page_roles)
        except (PageNotAnInteger, EmptyPage):
            page_obj_roles = paginator_roles.page(1)

        # --- Permisos adicionales ---
        permisos_qs = usuario.user_permissions.all().order_by('name')

        paginator_permisos = Paginator(permisos_qs, 4)
        page_permisos = request.GET.get('page_permisos', 1)
        try:
            page_obj_permisos = paginator_permisos.page(page_permisos)
        except (PageNotAnInteger, EmptyPage):
            page_obj_permisos = paginator_permisos.page(1)

        # querystring sin los parámetros de página
        querystring = request.GET.copy()
        for key in ('page_roles', 'page_permisos'):
            if key in querystring:
                querystring.pop(key)

        context = {
            'usuario': usuario,
            'roles':               page_obj_roles,
            'paginator_roles':     paginator_roles,
            'page_obj_roles':      page_obj_roles,
            'is_paginated_roles':  paginator_roles.num_pages > 1,
            'permisos':              page_obj_permisos,
            'paginator_permisos':    paginator_permisos,
            'page_obj_permisos':     page_obj_permisos,
            'is_paginated_permisos': paginator_permisos.num_pages > 1,
            'querystring': '&' + querystring.urlencode() if querystring else '',
        }

        return render(request, self.template_name, context)



class CrearUsuario(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Clase que permite la creación de un nuevo objeto en la base de datos.

    :param CreateView: Maneja la creacion de objetos
    :type CreateView: Objeto
    """

    model = Usuario
    form_class = RegistrarUsuarioForm
    template_name = 'gestion_usuarios/registrar_usuario.html'
    permission_required = 'gestion_usuarios.registrar_usuario'
    success_url = reverse_lazy('listar_usuarios')
    success_message = "El Usuario, fue creado exitosamente"

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
            general_message="No se pudo registrar el usuario. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        """Maneja formularios válidos"""
        self._clean_all_messages(self.request)  # Limpieza total garantizada

        response = super().form_valid(form)

        if self.object.pk:
            self.add_success_message(self.request, "El usuario registrado correctamente.")

        return response


class ActualizarUsuario(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Clase que permite la ctualización de los datos de un objeto específico.

    :param UpdateView: Manejar actualizaciones de objetos.
    :type UpdateView: Objeto
    """

    model = Usuario
    form_class = RegistrarUsuarioForm
    template_name= 'gestion_usuarios/registrar_usuario.html'
    permission_required = 'gestion_usuarios.registrar_usuario'
    success_url = reverse_lazy('listar_usuarios')
    success_message = "El Usuario, fue actualizado exitosamente"

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
            general_message="No se pudo registrar el Usuario. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        """Maneja formularios válidos"""
        self._clean_all_messages(self.request)  # Limpieza total garantizada

        response = super().form_valid(form)

        if self.object.pk:
            self.add_success_message(self.request, "El usuario actualizado correctamente.")

        return response


class EliminarUsuario(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'gestion_usuarios/eliminar_usuario.html'
    permission_required = 'gestion_usuarios.eliminar_usuario'
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        try:
            identificacion = self.object.identificacion
            result = super().form_valid(form)
            messages.success(self.request, f"El Usuario {identificacion} fue eliminado exitosamente")
            return result

        except ProtectedError:
            messages.error(
                self.request,
                f"No se pudo eliminar el Usuario {self.object.identificacion}. Tiene una relación."
            )
            return HttpResponseRedirect(self.success_url)

        except Exception as e:
            messages.error(
                self.request,
                f"Error inesperado al eliminar el Usuario: {str(e)}"
            )
            return HttpResponseRedirect(self.success_url)



######-------Crud de los roles-------######

class ListaRoles(LoginRequiredMixin, MultiplePermissionsRequiredMixin, ListView):
    """Clase para mostrar la lista de roles con filtros persistentes."""

    model = Group
    template_name = 'gestion_usuarios/listar_roles.html'
    context_object_name = 'roles'
    paginate_by = 10
    ordering = ['-id']
    permissions = {"any": (
        'gestion_usuarios.listar_roles',
        'gestion_usuarios.actualizar_rol',
        'gestion_usuarios.eliminar_rol',
        'gestion_usuarios.registrar_rol'
    )}

    def get_queryset(self):
        queryset = super().get_queryset()
        filtro_nombre = self.request.GET.get('nombre', '').strip()
        filtro_permiso = self.request.GET.get('permiso', '').strip()

        # 🔍 Filtrar por nombre del rol
        if filtro_nombre:
            queryset = queryset.filter(name__istartswith=filtro_nombre)

        # 🔍 Filtrar por nombre de permiso
        if filtro_permiso:
            queryset = queryset.filter(permissions__name__istartswith=filtro_permiso).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Guardar los filtros actuales para persistencia en el template
        context['filtro_nombre'] = self.request.GET.get('nombre', '')
        context['filtro_permiso'] = self.request.GET.get('permiso', '')

        # Construir querystring sin la parte de paginación para los links
        querystring = self.request.GET.copy()
        if 'page' in querystring:
            querystring.pop('page')
        context['querystring'] = '&' + querystring.urlencode() if querystring else ''
        return context




class CrearRol(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Clase que permite la creación de un nuevo objeto en la base de datos.

    :param CreateView: Maneja la creacion de objetos
    :type CreateView: Objeto
    """    
    
    model = Group
    form_class = RolForm
    template_name = 'gestion_usuarios/registrar_rol.html'
    permission_required = 'gestion_usuarios.registrar_rol'
    success_url = reverse_lazy('listar_roles')
    success_message = "El Rol, fue creado exitosamente"
    
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
            general_message="No se pudo registrar el Rol. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        """Maneja formularios válidos"""
        self._clean_all_messages(self.request)  # Limpieza total garantizada
    
        response = super().form_valid(form)
    
        if self.object.pk:
            self.add_success_message(self.request, "El rol actualizado correctamente.")
        else:
            self.add_success_message(self.request, "El rol registrado correctamente.")
    
        return response



class ActualizarRol(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Clase que permite la ctualización de los datos de un objeto específico.

    :param UpdateView: Manejar actualizaciones de objetos.
    :type UpdateView: Objeto 
    """       
    
    model = Group
    form_class = RolForm
    template_name= 'gestion_usuarios/registrar_rol.html'
    permission_required = 'gestion_usuarios.registrar_rol'
    success_url = reverse_lazy('listar_roles')
    success_message = "El Rol, fue actualizado exitosamente"
    
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
            general_message="No se pudo registrar el Rol. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        """Maneja formularios válidos"""
        self._clean_all_messages(self.request)  # Limpieza total garantizada
    
        response = super().form_valid(form)
    
        if self.object.pk:
            self.add_success_message(self.request, "El rol actualizado correctamente.")
        else:
            self.add_success_message(self.request, "El rol registrado correctamente.")
    
        return response


class EliminarRol(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Group
    template_name = 'gestion_usuarios/eliminar_rol.html'
    permission_required = 'gestion_usuarios.eliminar_rol'
    success_url = reverse_lazy('listar_roles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rol'] = self.object
        return context

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            if self.object.user_set.exists():
                messages.error(
                    self.request,
                    f"No se puede eliminar el rol '{self.object.name}'. "
                    "Tiene usuarios asignados."
                )
                return HttpResponseRedirect(self.success_url)

            self.object.delete()
            messages.success(self.request, "El Rol fue eliminado exitosamente.")
            return HttpResponseRedirect(self.success_url)

        except Exception as e:
            messages.error(
                self.request,
                f"Error inesperado al eliminar el Rol: {str(e)}"
            )
            return HttpResponseRedirect(self.success_url)


class BloquearUsuario(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'gestion_usuarios.bloquear_usuario'

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)

        usuario.estado = 'BL'
        usuario.fecha_bloqueo = timezone.now()
        usuario.motivo_bloqueo = 'admin'   # ← origen manual
        usuario.save(update_fields=['estado', 'fecha_bloqueo', 'motivo_bloqueo'])

        messages.success(
            request,
            f"El usuario {usuario.get_full_name() or usuario.username} fue bloqueado correctamente."
        )
        return redirect('listar_usuarios')


class InactivarUsuario(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'gestion_usuarios.inactivar_usuario'

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)

        usuario.estado = 'IN'
        usuario.is_active = False  # bloquea el login a nivel de Django también
        usuario.save(update_fields=['estado', 'is_active'])

        messages.success(
            request,
            f"El usuario {usuario.get_full_name() or usuario.username} fue inactivado correctamente."
        )
        return redirect('listar_usuarios')


class ActivarUsuario(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'gestion_usuarios.activar_usuario'

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)

        usuario.estado = 'AC'
        usuario.is_active = True
        usuario.intentos_fallidos = 0
        usuario.fecha_bloqueo = None
        usuario.save(update_fields=['estado', 'is_active', 'intentos_fallidos', 'fecha_bloqueo'])

        messages.success(
            request,
            f"El usuario {usuario.get_full_name() or usuario.username} fue activado correctamente."
        )
        return redirect('listar_usuarios')