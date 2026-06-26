from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, date


class Clientes(models.Model):
    
    """Creación de usuarios """
    TIPOS_ID = (
        ('', 'Seleccione el tipo de identificación'),
        ("C", "Cédula de ciudadanía"),
        ("N", "Nit"),
        ("TI", "Tarjeta de identidad"),
        ("RC", "Registro civil"),
        ("C.E.", "Cédula de extranjería"),
        ("C.N.", "Certificado de nacimiento"),
        ("PPN", "Pasaporte"),
        ("SSN", "Seguridad social"),
        ("DNI", "Documento nacional de identidad"),
        ("LIC", "Licencia"),
    )
    GENERO = (
        ('', 'Seleccione el tipo de Genero'),
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    )

    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de registro"
    )

    # --- CAMPOS AHORA ACEPTAN NULL Y BLANK ---
    nombre = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombres del Cliente'
    )

    apellido = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Apellidos del Cliente'
    )

    nombre_razon = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre / Razón Social'
    )

    tipo_identificacion = models.CharField(
        max_length=10,
        choices=TIPOS_ID,
        blank=True,
        null=True,
        verbose_name='Tipo Identificación'
    )

    identificacion = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Identificacion'
    )

    telefono = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )

    # --- EMAIL: Ya no es único ni obligatorio ---
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )
    # Si quieres mantener email único pero permitir NULL:
    # email = models.EmailField(blank=True, null=True, unique=True, verbose_name='Email')
    # Nota: Django permite NULL en campos únicos (solo uno puede ser NULL)

    genero = models.CharField(
        max_length=50,
        choices=GENERO,
        blank=True,
        null=True,
        verbose_name="Genero"
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dirección'
    )

    barrio = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Barrio'
    )

    negocio = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Negocio'
    )

    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad'
    )

    departamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento'
    )

    class Meta:
        default_permissions = ()
        permissions = (
            ('registrar_cliente', 'Puede Registrar Cliente'),
            ('listar_clientes', 'Puede Consultar clientes'),
            ('actualizar_cliente', 'Puede Actualizar cliente'),
            ('eliminar_cliente', 'Puede Eliminar cliente'),
            ('detalle_cliente', 'Puede Detalle cliente'),
            ('cargar_clientes', 'Puede Cargar Clientes desde Excel'),
        )

    def __str__(self):
        nombre_str = self.nombre if self.nombre else "Sin nombre"
        apellido_str = self.apellido if self.apellido else "Sin apellido"
        identificacion_str = self.identificacion if self.identificacion else "Sin identificación"
        return f"{nombre_str} - {apellido_str} - {identificacion_str}"
    
    @staticmethod
    def listar_clientes():
        return Clientes.objects.all()