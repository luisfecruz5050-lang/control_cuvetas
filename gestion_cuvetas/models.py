from django.db import models
from django.conf import settings
from django.utils import timezone
from gestion_clientes.models import *
from gestion_usuarios.models import *


class ControlCuvetas(models.Model):

    ESTADO_CHOICES = (
        ('', 'Seleccione un estado'),
        ('EN', 'Entregado'),
        ('PA', 'Parcialmente devuelto'),
        ('DE', 'Devuelto completo'),
        ('PE', 'Pendiente'),
    )

    # ── Relaciones ──────────────────────────────────────────────
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        editable=False,            # No aparece en el formulario; se llena en la vista
        verbose_name='Registrado por'
    )

    cliente = models.ForeignKey(
        Clientes,
        on_delete=models.PROTECT,
        verbose_name='Cliente'
    )

    # ── Fecha ────────────────────────────────────────────────────
    fecha_registro = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de registro'
    )

    # ── Cuvetas ──────────────────────────────────────────────────
    cuvetas_grandes = models.PositiveIntegerField(
        default=0,
        verbose_name='Cuvetas grandes'
    )

    cuvetas_pequenas = models.PositiveIntegerField(
        default=0,
        verbose_name='Cuvetas pequeñas'
    )

    # ── Estado y observaciones ───────────────────────────────────
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES,
        default='PE',
        verbose_name='Estado'
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    # ── Auditoría ────────────────────────────────────────────────
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # ── Propiedad calculada ──────────────────────────────────────
    @property
    def total_cuvetas(self):
        return (self.cuvetas_grandes or 0) + (self.cuvetas_pequenas or 0)

    class Meta:
        verbose_name = 'Control de cuvetas'
        verbose_name_plural = 'Control de cuvetas'
        ordering = ['-fecha_registro']
        default_permissions = ()
        permissions = (
            ('registrar_cuveta', 'Puede registrar control de cuvetas'),
            ('listar_cuvetas', 'Puede listar controles de cuvetas'),
            ('actualizar_cuveta', 'Puede actualizar control de cuvetas'),
            ('eliminar_cuveta', 'Puede eliminar control de cuvetas'),
            ('detalle_cuveta', 'Puede ver detalle de cuvetas'),
            ('actualizar_estado', 'Puede actualizar control de Estados'),
        )

    def __str__(self):
        return (
            f"{self.cliente.nombre} | "
            f"G:{self.cuvetas_grandes} P:{self.cuvetas_pequenas} | "
            f"{self.fecha_registro}"
        )