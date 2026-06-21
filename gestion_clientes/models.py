from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, date


class Clientes(models.Model):
    
    """Creación de usuarios """
    TIPOS_ID = (
        ('', 'Seleccione el tipo de identificación'),
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
        ('', 'Seleccione el tipo de Genero'),
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    )

    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de registro")
    nombre = models.CharField(max_length=100, verbose_name = 'Nombres del Cliente*')
    apellido = models.CharField(max_length=100, verbose_name = 'Apellidos del Cliente*')
    tipo_identificacion = models.CharField(max_length=10, choices=TIPOS_ID, verbose_name='Tipo Identificación')
    identificacion = models.CharField(max_length=10, verbose_name='Identificacion*')
    telefono = models.CharField(max_length=10, verbose_name='Teléfono*') 
    email = models.EmailField(unique=True, verbose_name='Email*')
    genero = models.CharField(max_length=50, choices=GENERO, verbose_name="Genero")
    
    class Meta:
        default_permissions = ()
        permissions = (
            ('registrar_cliente', 'Puede Registrar Cliente'),
            ('listar_clientes', 'Puede Consultar clientes'),
            ('actualizar_cliente', 'Puede Actualizar cliente'),
            ('eliminar_cliente', 'Puede Eliminar cliente'), 
            ('detalle_cliente', 'Puede Detalle cliente'),
        )
    
    def __str__(self):
        return  str(self.nombre) + ' - ' + str(self.apellido) + ' - ' + str(self.identificacion)
    
    @staticmethod
    def listar_clientes():
        return Clientes.objects.all()