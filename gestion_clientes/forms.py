from django import forms
from django.core.exceptions import ValidationError
from .models import Clientes
from django.utils import timezone
from datetime import datetime


class ClientesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ahora_bogota = timezone.localtime(timezone.now())
        self.fields['fecha_registro'].initial = ahora_bogota.strftime('%Y-%m-%dT%H:%M')

        # Marcar TODOS los campos como no requeridos
        for field_name, field in self.fields.items():
            field.required = False
            # Remover validadores adicionales si existen
            if hasattr(field, 'validators'):
                field.validators = []

    # --- TODOS LOS CAMPOS AHORA SON OPCIONALES Y SIN VALIDACIONES ---

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,  # ✅ Ya no es requerido
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingrese el correo electrónico (opcional)',
            'autocomplete': 'email',
        })
    )

    identificacion = forms.CharField(
        label="Número de Identificación",
        required=False,  # ✅ Ya no es requerido
        max_length=13,   # Se mantiene por estructura pero no valida
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese la identificación (opcional)',
        })
    )

    telefono = forms.CharField(
        label="Teléfono",
        required=False,  # ✅ Ya no es requerido
        max_length=10,   # Se mantiene por estructura pero no valida
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el número de teléfono (opcional)',
        })
    )

    nombre_razon = forms.CharField(
        label="Nombre / Razón Social",
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el nombre o razón social (opcional)',
        })
    )

    negocio = forms.CharField(
        label="Negocio",
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el nombre del negocio (opcional)',
        })
    )

    direccion = forms.CharField(
        label="Dirección",
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Calle 10 # 5-23 (opcional)',
        })
    )

    barrio = forms.CharField(
        label="Barrio",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el barrio (opcional)',
        })
    )

    ciudad = forms.CharField(
        label="Ciudad",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese la ciudad (opcional)',
        })
    )

    departamento = forms.CharField(
        label="Departamento",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el departamento (opcional)',
        })
    )

    class Meta:
        model = Clientes
        fields = [
            'fecha_registro',
            'nombre',
            'apellido',
            'nombre_razon',
            'tipo_identificacion',
            'identificacion',
            'telefono',
            'email',
            'genero',
            'negocio',
            'direccion',
            'barrio',
            'ciudad',
            'departamento',
        ]
        widgets = {
            'fecha_registro': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'readonly': 'readonly',
                }
            ),
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ingrese el nombre del cliente (opcional)'
            }),
            'apellido': forms.TextInput(attrs={
                'placeholder': 'Ingrese el apellido del cliente (opcional)'
            }),
            'tipo_identificacion': forms.Select(attrs={
                'class': 'form-control'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
