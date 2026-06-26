from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse          # ← añadido HttpResponse
from django.urls import reverse_lazy
from django.views import View                                        # ← nuevo
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
import openpyxl                                                      # ← nuevo
from django.core.validators import validate_email                    # ← nuevo
from django.core.exceptions import ValidationError                  # ← nuevo


####--------Vistas del curso--------####
class ListaClientes(LoginRequiredMixin, MultiplePermissionsRequiredMixin, ListView):
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
            'gestion_clientes.detalle_cliente',
            'gestion_clientes.cargar_clientes',    # ← nuevo
        )
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        filtro_nombre         = self.request.GET.get('nombre', '').strip()
        filtro_apellido       = self.request.GET.get('apellido', '').strip()
        filtro_identificacion = self.request.GET.get('identificacion', '').strip()
        filtro_telefono       = self.request.GET.get('telefono', '').strip()
        filtro_email          = self.request.GET.get('email', '').strip()
        filtro_genero         = self.request.GET.get('genero', '').strip()

        if filtro_nombre:
            queryset = queryset.filter(nombre__istartswith=filtro_nombre)
        if filtro_apellido:
            queryset = queryset.filter(apellido__istartswith=filtro_apellido)
        if filtro_identificacion:
            if filtro_identificacion.isdigit():
                queryset = queryset.filter(identificacion__istartswith=filtro_identificacion)
            else:
                queryset = queryset.none()
        if filtro_telefono:
            if filtro_telefono.isdigit():
                queryset = queryset.filter(telefono__istartswith=filtro_telefono)
            else:
                queryset = queryset.none()
        if filtro_email:
            queryset = queryset.filter(email__istartswith=filtro_email)
        if filtro_genero:
            queryset = queryset.filter(genero__istartswith=filtro_genero)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_nombre']         = self.request.GET.get('nombre', '')
        context['filtro_apellido']       = self.request.GET.get('apellido', '')
        context['filtro_identificacion'] = self.request.GET.get('identificacion', '')
        context['filtro_telefono']       = self.request.GET.get('telefono', '')
        context['filtro_email']          = self.request.GET.get('email', '')
        context['filtro_genero']         = self.request.GET.get('genero', '')
        querystring = self.request.GET.copy()
        if 'page' in querystring:
            querystring.pop('page')
        context['querystring'] = '&' + querystring.urlencode() if querystring else ''
        return context


# ─────────────────────────────────────────────────────────────────────────────
# CARGUE MASIVO DESDE EXCEL
# ─────────────────────────────────────────────────────────────────────────────

# Cabeceras esperadas en el Excel (en minúsculas, sin espacios)
_CABECERAS_EXCEL = [
    'nombre', 'apellido', 'nombre_razon', 'tipo_identificacion',
    'identificacion', 'telefono', 'email', 'genero',
    'direccion', 'barrio', 'negocio', 'ciudad', 'departamento',
]


class CargueClientesExcel(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Recibe un archivo Excel (.xlsx) y crea registros de Clientes masivamente.
    El POST se envía desde el modal en listar_clientes.html.
    """
    permission_required = 'gestion_clientes.cargar_clientes'

    def get(self, request, *args, **kwargs):
        # El formulario vive en el modal de listar_clientes; no hay página propia
        return redirect('listar_clientes')

    def post(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo_excel')

        # ── Validaciones de archivo ──────────────────────────────────────────
        if not archivo:
            messages.error(request, "No se seleccionó ningún archivo.")
            return redirect('listar_clientes')

        if not archivo.name.lower().endswith(('.xlsx', '.xls')):
            messages.error(request, "El archivo debe ser un Excel válido (.xlsx o .xls).")
            return redirect('listar_clientes')

        try:
            wb = openpyxl.load_workbook(archivo, data_only=True)
            ws = wb.active
        except Exception as e:
            messages.error(request, f"No se pudo leer el archivo: {str(e)}")
            return redirect('listar_clientes')

        filas = list(ws.iter_rows(values_only=True))

        if not filas:
            messages.error(request, "El archivo está vacío.")
            return redirect('listar_clientes')

        # ── Validar cabeceras ────────────────────────────────────────────────
        cabeceras_archivo = [
            str(c).strip().lower() if c is not None else ''
            for c in filas[0]
        ]
        cabeceras_faltantes = [h for h in _CABECERAS_EXCEL if h not in cabeceras_archivo]
        if cabeceras_faltantes:
            messages.error(
                request,
                f"El archivo no tiene las columnas requeridas: {', '.join(cabeceras_faltantes)}. "
                "Descarga la plantilla para ver el formato correcto."
            )
            return redirect('listar_clientes')

        # Mapeo nombre_columna → índice
        idx = {h: cabeceras_archivo.index(h) for h in _CABECERAS_EXCEL}

        # ── Procesar filas ───────────────────────────────────────────────────
        creados  = 0
        errores  = []           # lista de strings con descripción del error
        omitidas = 0            # filas completamente vacías

        for num_fila, fila in enumerate(filas[1:], start=2):

            def col(nombre):
                """Devuelve el valor de la celda como string limpio o ''."""
                val = fila[idx[nombre]]
                return str(val).strip() if val is not None else ''

            # Omitir filas vacías
            if all(c is None or str(c).strip() == '' for c in fila):
                omitidas += 1
                continue

            # ── Obtener datos del Excel ──────────────────────────────────────
            nombre = col('nombre') or None
            apellido = col('apellido') or None
            tipo_id = col('tipo_identificacion') or None
            identificacion = col('identificacion') or None
            telefono = col('telefono') or None
            email = col('email') or None
            genero = col('genero') or None

            nombre_razon = col('nombre_razon') or None
            direccion = col('direccion') or None
            barrio = col('barrio') or None
            negocio = col('negocio') or None
            ciudad = col('ciudad') or None
            departamento = col('departamento') or None

            # ── Crear registro ───────────────────────────────────────────────
            try:
                Clientes.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    nombre_razon=nombre_razon,
                    tipo_identificacion=tipo_id,
                    identificacion=identificacion,
                    telefono=telefono,
                    email=email,
                    genero=genero,
                    direccion=direccion,
                    barrio=barrio,
                    negocio=negocio,
                    ciudad=ciudad,
                    departamento=departamento,
                )
                creados += 1
            except Exception as e:
                errores.append(f"Fila {num_fila}: error al guardar — {str(e)}")

        # ── Mensajes de resultado ────────────────────────────────────────────
        if creados:
            messages.success(request, f"{creados} cliente(s) cargado(s) exitosamente.")

        if errores:
            # Mostramos máximo 10 errores para no saturar la UI
            for err in errores[:10]:
                messages.warning(request, err)
            if len(errores) > 10:
                messages.warning(
                    request,
                    f"… y {len(errores) - 10} error(es) adicionales. Corrige el archivo y vuelve a cargarlo."
                )

        if not creados and not errores:
            messages.info(request, "No se encontraron filas con datos para cargar.")

        return redirect('listar_clientes')


class DescargarPlantillaClientes(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Genera y descarga un Excel vacío con las columnas requeridas
    y una fila de ejemplo para orientar al usuario.
    """
    permission_required = 'gestion_clientes.cargar_clientes'

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Clientes"

        # ── Cabeceras ────────────────────────────────────────────────────────
        ws.append(_CABECERAS_EXCEL)

        # Estilo de cabecera (fondo oscuro, texto blanco, negrita)
        from openpyxl.styles import PatternFill, Font, Alignment
        header_fill = PatternFill(start_color="1E3A5F", end_color="1E3A5F", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in ws[1]:
            cell.fill      = header_fill
            cell.font      = header_font
            cell.alignment = Alignment(horizontal="center")

        # ── Fila de ejemplo ──────────────────────────────────────────────────
        ws.append([
            'Juan',           # nombre
            'Pérez',          # apellido
            'Tienda JuanP',   # nombre_razon  (opcional)
            'CC',             # tipo_identificacion
            '1234567890',     # identificacion
            '3001234567',     # telefono
            'juan@ejemplo.com',# email
            'M',              # genero
            'Calle 5 # 10-20',# direccion     (opcional)
            'El Centro',      # barrio        (opcional)
            'Droguería',      # negocio       (opcional)
            'Cali',           # ciudad        (opcional)
            'Valle del Cauca',# departamento  (opcional)
        ])

        # ── Ancho automático de columnas ─────────────────────────────────────
        for col in ws.columns:
            max_len = max(len(str(c.value)) if c.value else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = max_len + 4

        # ── Respuesta HTTP ───────────────────────────────────────────────────
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="plantilla_clientes.xlsx"'
        wb.save(response)
        return response


# ─────────────────────────────────────────────────────────────────────────────
# Vistas CRUD existentes (sin cambios)
# ─────────────────────────────────────────────────────────────────────────────

class DetalleCliente(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Clientes
    template_name = 'gestion_clientes/detalle_cliente.html'
    permission_required = 'gestion_clientes.detalle_cliente'
    success_url = reverse_lazy('clientes')


class CrearCliente(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Clientes
    form_class = ClientesForm
    template_name = 'gestion_clientes/registrar_cliente.html'
    permission_required = 'gestion_clientes.registrar_cliente'
    success_url = reverse_lazy('listar_clientes')
    success_message = "El Cliente fue registrado exitosamente"

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

    def form_invalid(self, form):
        self.add_error_messages(
            request=self.request,
            form=form,
            general_message="No se pudo registrar el Cliente. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        self._clean_all_messages(self.request)
        response = super().form_valid(form)
        if self.object.pk:
            self.add_success_message(self.request, "Cliente registrado correctamente.")
        return response


class ActualizarCliente(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Clientes
    form_class = ClientesForm
    template_name = 'gestion_clientes/registrar_cliente.html'
    permission_required = 'gestion_clientes.registrar_cliente'
    success_url = reverse_lazy('listar_clientes')
    success_message = "El Cliente fue actualizado exitosamente"

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

    def form_invalid(self, form):
        self.add_error_messages(
            request=self.request,
            form=form,
            general_message="No se pudo registrar el Cliente. Por favor, revise los datos."
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        self._clean_all_messages(self.request)
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
            nombre = self.object.nombre
            result = super().form_valid(form)
            messages.success(self.request, f"El Cliente {nombre} fue eliminado exitosamente")
            return result
        except ProtectedError:
            messages.error(
                self.request,
                f"No se pudo eliminar el Cliente {self.object.nombre}. Tiene facturas asociadas."
            )
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error inesperado al eliminar el Cliente: {str(e)}")
            return HttpResponseRedirect(self.success_url)