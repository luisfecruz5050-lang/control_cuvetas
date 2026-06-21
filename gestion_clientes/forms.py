from django import forms
from django.core.exceptions import ValidationError
from .models import Clientes
from django.utils import timezone
from datetime import datetime


class ClientesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ahora: localtime() convierte UTC → America/Bogota
        ahora_bogota = timezone.localtime(timezone.now())
        self.fields['fecha'].initial = ahora_bogota.strftime('%Y-%m-%dT%H:%M')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fecha automática
        ahora_bogota = timezone.localtime(timezone.now())
        self.fields['fecha_registro'].initial = ahora_bogota.strftime('%Y-%m-%dT%H:%M')
        # Empty labels
        self.fields['tipo_identificacion'].empty_label = "Seleccione el tipo de identificación"
        self.fields['genero'].empty_label = "Seleccione el género"

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        error_messages={
            "required": "Debe ingresar un correo electrónico.",
            "invalid": "El formato del correo no es válido. Ejemplo: cliente@dominio.com"
        },
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingrese el correo electrónico',
            'autocomplete': 'email',
        })
    )

    identificacion = forms.CharField(
        label="Número de Identificación",
        max_length=13,
        min_length=6,
        error_messages={
            'required'  : 'Debe ingresar una identificación.',
            'max_length': 'El número de identificación debe tener maximo 12 dígitos.',
            'min_length': 'El número de identificación debe ser mayor a 6 dígitos.',
        },
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ingrese la identificación',
        })
    )

    telefono = forms.CharField(
        label="Teléfono",
        max_length=10,
        min_length=10,
        error_messages={
            'required'  : 'Debe ingresar un numero telefonico.',
            'max_length': 'El número de teléfono debe tener exactamente 10 dígitos.',
            'min_length': 'El número de teléfono debe tener exactamente 10 dígitos.',
        },
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ingrese el número de teléfono',
        })
    )

    class Meta:
        model = Clientes
        fields = [
            'fecha_registro',
            'nombre',
            'apellido',
            'tipo_identificacion',
            'identificacion',
            'telefono',
            'email',
            'genero'
        ]
        widgets = {
            'fecha_registro': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',  # ← Añade esto también
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'readonly': 'readonly',
                }
            ),
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ingrese el nombre del cliente'
            }),
            'apellido': forms.TextInput(attrs={
                'placeholder': 'Ingrese el apellido del cliente'
            }),
        }

    # --------------------------
    # VALIDACIONES PERSONALIZADAS
    # --------------------------

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellido = cleaned_data.get('apellido')
        if nombre and apellido:
            qs = Clientes.objects.filter(nombre=nombre, apellido=apellido)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({'nombre': 'Ya existe un cliente con este nombre y apellido.'})
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        qs = Clientes.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("El correo electrónico ya se encuentra registrado en el sistema.")
        return email

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get("identificacion")
        qs = Clientes.objects.filter(identificacion=identificacion)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un Cliente con esa identificación.")
        return identificacion