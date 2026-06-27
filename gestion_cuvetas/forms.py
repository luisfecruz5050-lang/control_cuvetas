from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ControlCuvetas, Clientes


class ControlCuvetasForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fecha se llena automáticamente con hoy
        self.fields['fecha_registro'].initial = timezone.localdate()

        # Solo el cliente es obligatorio además de las cuvetas
        campos_opcionales = ['observaciones']
        for field_name in campos_opcionales:
            self.fields[field_name].required = False

        # Ordenar el queryset del cliente por nombre
        self.fields['cliente'].queryset = Clientes.objects.all().order_by('nombre', 'apellido')
        self.fields['cliente'].empty_label = 'Seleccione un cliente'

    # ── Campos ──────────────────────────────────────────────────

    cliente = forms.ModelChoiceField(
        queryset=Clientes.objects.all(),
        label='Cliente',
        widget=forms.Select(attrs={
            'class': 'form-control select2',   # select2 si lo usas
            'placeholder': 'Buscar cliente...',
        })
    )

    cuvetas_grandes = forms.IntegerField(
        label='Cuvetas grandes',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'min': '0',
        })
    )

    cuvetas_pequenas = forms.IntegerField(
        label='Cuvetas pequeñas',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'min': '0',
        })
    )

    observaciones = forms.CharField(
        label='Observaciones',
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 2 cuvetas grandes en mal estado, pendiente revisión...',
            'rows': 3,
            'maxlength': '500',
        })
    )

    # ── Validaciones individuales (clean_<campo>) ────────────────

    def clean_cuvetas_grandes(self):
        valor = self.cleaned_data.get('cuvetas_grandes')
        if valor is None:
            raise ValidationError('Este campo es obligatorio.')
        if valor < 0:
            raise ValidationError('La cantidad no puede ser negativa.')
        if valor > 9999:
            raise ValidationError('La cantidad máxima permitida es 9.999.')
        return valor

    def clean_cuvetas_pequenas(self):
        valor = self.cleaned_data.get('cuvetas_pequenas')
        if valor is None:
            raise ValidationError('Este campo es obligatorio.')
        if valor < 0:
            raise ValidationError('La cantidad no puede ser negativa.')
        if valor > 9999:
            raise ValidationError('La cantidad máxima permitida es 9.999.')
        return valor

    def clean_fecha_registro(self):
        fecha = self.cleaned_data.get('fecha_registro')
        if not fecha:
            raise ValidationError('La fecha es obligatoria.')
        hoy = timezone.localdate()
        if fecha > hoy:
            raise ValidationError('La fecha de registro no puede ser futura.')
        # No permitir registros con más de 1 año de antigüedad
        from datetime import timedelta
        if fecha < hoy - timedelta(days=365):
            raise ValidationError('La fecha no puede tener más de un año de antigüedad.')
        return fecha

    def clean_observaciones(self):
        obs = self.cleaned_data.get('observaciones', '')
        if obs:
            obs = obs.strip()
            if len(obs) < 5:
                raise ValidationError('Si escribe una observación, debe tener al menos 5 caracteres.')
        return obs

    # ── Validación cruzada (clean general) ───────────────────────

    def clean(self):
        cleaned_data = super().clean()
        grandes = cleaned_data.get('cuvetas_grandes', 0)
        pequenas = cleaned_data.get('cuvetas_pequenas', 0)
        estado = cleaned_data.get('estado')

        # Al menos una cuveta debe ser mayor a 0
        if (grandes is not None and pequenas is not None):
            if grandes == 0 and pequenas == 0:
                raise ValidationError(
                    'Debe registrar al menos una cuveta (grande o pequeña).'
                )

        # Si el estado es "Devuelto completo", advertir que se registrará con 0 pendientes
        # (lógica de negocio: no tiene sentido devolver si nunca se entregó)
        if estado == 'DE' and grandes == 0 and pequenas == 0:
            raise ValidationError(
                'No puede marcar "Devuelto completo" sin haber registrado cuvetas entregadas.'
            )

        return cleaned_data

    class Meta:
        model = ControlCuvetas
        fields = [
            'cliente',
            'fecha_registro',
            'cuvetas_grandes',
            'cuvetas_pequenas',
            'estado',
            'observaciones',
        ]
        widgets = {
            'fecha_registro': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'readonly': 'readonly',  # Se llena automáticamente
                }
            ),
        }