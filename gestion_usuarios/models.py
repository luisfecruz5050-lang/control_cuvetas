from django.db import models
from django.contrib.auth.models import Permission, AbstractUser
from django.utils import timezone


class Usuario(AbstractUser):

    """Creación de usuarios """
    TIPOS_ID = (
        ("CC", "Cédula de ciudadanía"),
        ("TI", "Tarjeta de identidad"),
        ("RC", "Registro civil"),
        ("CE", "Cédula de extranjería"),
        ("PPN", "Pasaporte"),
        ("SSN", "Seguridad social"),
        ("DNI", "Documento nacional de identidad"),
        ("LIC", "Licencia"),
    )
    GENERO = (
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    )

    ESTADOS = (
        ("AC", "Activo"),
        ("BL", "Bloqueado"),
        ("IN", "Inactivo"),
    )

    MOTIVOS_BLOQUEO = (
        ("intentos", "Múltiples intentos fallidos"),
        ("admin",    "Bloqueado por administrador"),
    )

    tipo_identificacion = models.CharField(max_length=10, choices=TIPOS_ID, verbose_name='Tipo Identificación')
    identificacion      = models.CharField(max_length=20, null=False, blank=True, default="")
    telefono            = models.CharField(max_length=10, verbose_name='Teléfono')
    ciudad              = models.CharField(max_length=200, verbose_name='Ciudad')
    genero              = models.CharField(max_length=50, choices=GENERO, verbose_name="Genero")

    # --- Control de estado y acceso ---
    estado          = models.CharField(max_length=2, choices=ESTADOS, default="AC", verbose_name="Estado")
    intentos_fallidos = models.PositiveIntegerField(default=0, verbose_name='Intentos Fallidos')
    fecha_bloqueo   = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Bloqueo')
    motivo_bloqueo  = models.CharField(max_length=10, choices=MOTIVOS_BLOQUEO, null=True, blank=True, verbose_name='Motivo de Bloqueo')

    MAX_INTENTOS = 3

    class Meta:
        ordering = ['-first_name']
        default_permissions = ()
        permissions = (
            ('registrar_usuario', 'Puede Registrar Usuario'),
            ('listar_usuarios',   'Puede Consultar Usuarios'),
            ('actualizar_usuario','Puede Actualizar Usuario'),
            ('eliminar_usuario',  'Puede Eliminar Usuario'),
            ('detalle_usuario',   'Puede Ver Detalle Usuario'),
            ('usuario_usuario',   'Puede Ver el Usuario'),
            ('bloquear_usuario',  'Puede Bloquear Usuario'),
            ('inactivar_usuario', 'Puede Inactivar Usuario'),
            ('activar_usuario',   'Puede Activar Usuario'),
        )

    def save(self, *args, **kwargs):
        if self.email:
            self.username = self.email

        if not self.pk and not self.password:
            self.set_password(str(self.identificacion))

        if self.pk:
            original = Usuario.objects.get(pk=self.pk)
            if original.identificacion != self.identificacion:
                self.set_password(str(self.identificacion))

        super(Usuario, self).save(*args, **kwargs)

    def registrar_intento_fallido(self):
        """Suma un intento fallido y bloquea automáticamente si llega al máximo."""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= self.MAX_INTENTOS:
            self.estado         = "BL"
            self.fecha_bloqueo  = timezone.now()
            self.motivo_bloqueo = "intentos"   # ← origen automático
        self.save(update_fields=['intentos_fallidos', 'estado', 'fecha_bloqueo', 'motivo_bloqueo'])

    def resetear_intentos(self):
        """Limpia el contador, reactiva al usuario y borra el motivo de bloqueo."""
        if self.intentos_fallidos != 0 or self.estado == "BL":
            self.intentos_fallidos = 0
            self.estado            = "AC"
            self.fecha_bloqueo     = None
            self.motivo_bloqueo    = None      # ← limpia el motivo al activar
            self.save(update_fields=['intentos_fallidos', 'estado', 'fecha_bloqueo', 'motivo_bloqueo'])


class Roles(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ('registrar_rol',  'Puede Registrar Rol'),
            ('listar_roles',   'Puede Consultar Roles'),
            ('actualizar_rol', 'Puede Actualizar Rol'),
            ('eliminar_rol',   'Puede eliminar Rol'),
        )