from django import forms
from django.contrib.auth.models import Group, Permission
from django.db.models import Case, When
from django.core.exceptions import ValidationError
from .models import Usuario
from .listado_permisos import LISTADO_PERMISOS


class RegistrarUsuarioForm(forms.ModelForm):

    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        error_messages={
            "required": "Debe ingresar un correo electrónico.",
            "invalid": "El formato del correo no es válido. Ejemplo: usuario@dominio.com"
        },
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingrese su correo electrónico'
        })
    )
    tipo_identificacion = forms.ChoiceField(
        choices=[('', 'Seleccione tipo de identificación')] + list(Usuario.TIPOS_ID),
    )

    identificacion = forms.CharField(
        label="Número de Identificación",
        max_length=12,
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

    genero = forms.ChoiceField(
        choices=[('', 'Seleccione género')] + list(Usuario.GENERO),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Roles asignados"
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Permisos adicionales"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ordenar permisos
        orden = Case(*[
            When(codename=codename, then=pos)
            for pos, codename in enumerate(LISTADO_PERMISOS)
        ])
        perms = Permission.objects.filter(
            codename__in=LISTADO_PERMISOS
        ).order_by(orden)

        self.fields["user_permissions"].queryset = perms

        # Agrupar permisos por módulo
        self.permisos_agrupados = {}
        for p in perms:
            modulo = p.content_type.app_label
            self.permisos_agrupados.setdefault(modulo, []).append(p)

    class Meta:
        model = Usuario
        fields = (
            "tipo_identificacion", "identificacion",
            "first_name", "last_name", "email",
            "genero", "ciudad", "telefono",
            "groups", "user_permissions"
        )
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Ingrese el nombre del cliente',
                'required': True,
                'required': 'Ingrese el nombre del usuario',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Ingrese el apellido del usuario',
                'required': True,
                'required': 'Ingrese el apellido del usuario',
            }),
            'ciudad': forms.TextInput(attrs={
                'placeholder': 'Ingrese una ciudad',
                'required': True,
                'required': 'Ingrese la ciudad del usuario',
            }),

        }


    # --------------------------
    # VALIDACIONES PERSONALIZADAS
    # --------------------------

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get("identificacion")
        qs = Usuario.objects.filter(identificacion=identificacion)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un Usuario con esa identificación.")
        return identificacion

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        qs = Usuario.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este correo electrónico ya está registrado en el sistema.')
        return email

    def clean_groups(self):
        groups = self.cleaned_data.get("groups")
        if not groups or len(groups) == 0:
            raise ValidationError("Debe seleccionar al menos un rol.")
        return groups



class LoginForm(forms.Form):
    username = forms.CharField(
        label="Correo Electrónico",
        max_length=80,
        required=True,
        error_messages={
            "required": "Debe ingresar su correo electrónico."
        },
        widget=forms.TextInput(attrs={
            'id': 'usernameInput',
            'placeholder': 'Correo Electrónico',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        max_length=50,
        required=True,
        error_messages={
            "required": "Debe ingresar su contraseña."
        },
        widget=forms.PasswordInput(attrs={
            'id': 'passwordInput',
            'placeholder': 'Contraseña',
            'class': 'form-control'
        })
    )


class RolForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ("name", "permissions")

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del rol",
                "required": "required"
            }),
            "permissions": forms.CheckboxSelectMultiple(),
        }

        error_messages = {
            "permissions": {
                "required": "Debes seleccionar al menos un permiso.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].label = "Nombre del Rol"
        self.fields["permissions"].label = "Permisos Asignados al Rol"

        # Hacer que el campo sea obligatorio en Django
        self.fields["permissions"].required = True

        # ---------------------------
        # 1. FILTRAR SOLO TUS PERMISOS
        # ---------------------------
        orden = Case(*[
            When(codename=codename, then=pos)
            for pos, codename in enumerate(LISTADO_PERMISOS)
        ])

        permisos_filtrados = (
            Permission.objects
            .filter(codename__in=LISTADO_PERMISOS)
            .order_by(orden)
        )

        self.fields["permissions"].queryset = permisos_filtrados

        # -------------------------------
        # 2. AGRUPAR PERMISOS POR MÓDULO
        # -------------------------------
        grupos = {}
        for p in permisos_filtrados:
            grupos.setdefault(p.content_type.app_label, []).append(p)

        self.permisos_agrupados = grupos  # requerido por el template


    def clean_name(self):
        name = self.cleaned_data.get("name").strip()

        if not name:
            raise ValidationError("El nombre del rol es obligatorio")

        queryset = Group.objects.filter(name__iexact=name)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError("Ya existe un rol con este nombre")

        return name


    def clean_permissions(self):
        permissions = self.cleaned_data.get("permissions")

        if not permissions:
            raise ValidationError("Debes seleccionar al menos un permiso para el rol.")

        return permissions
