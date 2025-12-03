from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password, password_validators_help_text_html
from django.core.exceptions import ValidationError
from .models import (
    Farmacia, Motorista, Moto, ContactoEmergencia, 
    AsignacionFarmacia, AsignacionMoto, Documentacion, DocumentacionMoto,
    Mantenimiento, TipoMovimiento, Movimiento,
    Usuario, Rol, Region, Provincia, Comuna
)

# --- WIDGETS NATIVOS ---
class NativeDateInput(forms.DateInput):
    """Widget personalizado para renderizar inputs de tipo 'date' de HTML5."""
    input_type = 'date'
    def __init__(self, attrs=None, format='%Y-%m-%d'):
        super().__init__(attrs, format=format)
        self.attrs['class'] = 'form-control'


class NativeTimeInput(forms.TimeInput):
    """Widget personalizado para renderizar inputs de tipo 'time' de HTML5."""
    input_type = 'time'
    def __init__(self, attrs=None, format='%H:%M'):
        super().__init__(attrs, format=format)
        self.attrs['class'] = 'form-control'

class NativeDateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    def __init__(self, attrs=None, format='%Y-%m-%dT%H:%M'):
        super().__init__(attrs, format=format)
        self.attrs['class'] = 'form-control'

# --- FORMULARIOS DE AUTENTICACIÓN ---

class CustomLoginForm(AuthenticationForm):
    """Formulario de inicio de sesión."""
    username = forms.CharField(
        label="Usuario o Correo",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nombre de usuario o Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Contraseña',
            'autocomplete': 'off'
        })
    )

class UsuarioForm(forms.ModelForm):
    """
    Formulario para Crear/Editar usuarios con validación de seguridad completa.
    """
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'placeholder': 'Ingrese contraseña segura'
        }),
        required=False,
        help_text=password_validators_help_text_html() 
    )
    
    confirmar_contrasena = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'placeholder': 'Repita la contraseña'
        }),
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email', 
            'rut', 'telefono', 'rol', 'is_active', 
            'password', 'confirmar_contrasena'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario (Login)'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+569... (Opcional)'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos obligatorios
        campos_obligatorios = ['first_name', 'last_name', 'email', 'rut', 'rol']
        for campo in campos_obligatorios:
            self.fields[campo].required = True
            if 'placeholder' in self.fields[campo].widget.attrs:
                self.fields[campo].widget.attrs['placeholder'] += ' *'

        self.fields['telefono'].required = False

        if not self.instance.pk:
            self.fields['password'].required = True
            self.fields['confirmar_contrasena'].required = True

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirmar_contrasena')
        
        if p1 or p2:
            # 1. Verificar coincidencia
            if p1 != p2:
                self.add_error('confirmar_contrasena', "Las contraseñas no coinciden.")
            else:
                try:
                    validate_password(p1, self.instance)
                except ValidationError as error:
                    self.add_error('password', error)
                    
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get('password')
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
        return user

# --- FORMULARIOS MODULOS ---
# --- Farmacia ---
class FarmaciaForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Región",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.none(),
        label="Provincia",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Farmacia
        fields = [
            'nombre', 'direccion', 'region', 'provincia', 'comuna', 
            'horario_apertura', 'horario_cierre', 'telefono', 
            'latitud', 'longitud'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'horario_apertura': NativeTimeInput(),
            'horario_cierre': NativeTimeInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['comuna'].queryset = Comuna.objects.none()

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['provincia'].queryset = Provincia.objects.filter(region_id=region_id).order_by('nombreProvincia')
            except (ValueError, TypeError):
                pass
        
        if 'provincia' in self.data:
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['comuna'].queryset = Comuna.objects.filter(provincia_id=provincia_id).order_by('nombreComuna')
            except (ValueError, TypeError):
                pass

        if self.instance.pk and self.instance.comuna:
            self.fields['comuna'].queryset = Comuna.objects.filter(provincia=self.instance.comuna.provincia)
            self.fields['provincia'].queryset = Provincia.objects.filter(region=self.instance.comuna.provincia.region)
        
            self.initial['comuna'] = self.instance.comuna
            self.initial['provincia'] = self.instance.comuna.provincia
            self.initial['region'] = self.instance.comuna.provincia.region

class MotoristaForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Región",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.none(),
        label="Provincia",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Motorista
        fields = [
            'codigo',
            'rut', 'pasaporte', 'nombres', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 
            'region', 'provincia', 
            'comuna', 'direccion', 
            'telefono', 'correo',
            'incluye_moto_personal',
            'estado',
            'licencia_conducir', 'fecha_ultimo_control', 'fecha_proximo_control'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'pasaporte': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'comuna': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'incluye_moto_personal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'licencia_conducir': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': NativeDateInput(attrs={'class': 'form-control'}),
            'fecha_ultimo_control': NativeDateInput(attrs={'class': 'form-control'}),
            'fecha_proximo_control': NativeDateInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

        self.fields['comuna'].queryset = Comuna.objects.none()

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['provincia'].queryset = Provincia.objects.filter(region_id=region_id).order_by('nombreProvincia')
            except (ValueError, TypeError):
                pass
        
        if 'provincia' in self.data:
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['comuna'].queryset = Comuna.objects.filter(provincia_id=provincia_id).order_by('nombreComuna')
            except (ValueError, TypeError):
                pass

        if self.instance.pk and self.instance.comuna:
            self.fields['comuna'].queryset = Comuna.objects.filter(provincia=self.instance.comuna.provincia)
            self.fields['provincia'].queryset = Provincia.objects.filter(region=self.instance.comuna.provincia.region)
            
            self.initial['comuna'] = self.instance.comuna
            self.initial['provincia'] = self.instance.comuna.provincia
            self.initial['region'] = self.instance.comuna.provincia.region

class MotoForm(forms.ModelForm):
    """Formulario para la gestión de Motos."""
    class Meta:
        model = Moto
        fields = [
            'patente', 'marca', 'modelo', 'color', 'anio', 
            'numero_chasis', 'motor', 'propietario'
        ]
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AA-BB-12'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_chasis': forms.TextInput(attrs={'class': 'form-control'}),
            'motor': forms.TextInput(attrs={'class': 'form-control'}),
            'propietario': forms.Select(attrs={'class': 'form-select'}),
        }

class ContactoEmergenciaForm(forms.ModelForm):
    """Formulario para registrar contactos de emergencia."""
    class Meta:
        model = ContactoEmergencia
        fields = ['nombreCompleto', 'parentesco', 'telefono']

class DocumentacionForm(forms.ModelForm):
    """Formulario para documentos generales del motorista."""
    class Meta:
        model = Documentacion
        fields = ['nombreDocumento', 'archivo', 'fechaVencimiento']

class DocumentacionMotoForm(forms.ModelForm):
    """
    Formulario para actualizar los documentos de una moto.
    Incluye validación de fechas y subida de archivos.
    """
    class Meta:
        model = DocumentacionMoto
        exclude = ['moto'] 
        widgets = {
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'permiso_circulacion_file': forms.FileInput(attrs={'class': 'form-control'}),
            'permiso_circulacion_vencimiento': NativeDateInput(),
            'seguro_obligatorio_file': forms.FileInput(attrs={'class': 'form-control'}),
            'seguro_obligatorio_vencimiento': NativeDateInput(),
            'revision_tecnica_file': forms.FileInput(attrs={'class': 'form-control'}),
            'revision_tecnica_vencimiento': NativeDateInput(),
        }

class MantenimientoForm(forms.ModelForm):
    """Formulario para registrar mantenimientos de vehículos."""
    class Meta:
        model = Mantenimiento
        exclude = ['moto'] 
        widgets = {
            'fecha_mantenimiento': NativeDateInput(),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'taller': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
            'factura': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
# --- Movimientos ---
class TipoMovimientoForm(forms.ModelForm):
    """Formulario para gestionar los tipos de movimiento."""
    class Meta:
        model = TipoMovimiento
        fields = '__all__'

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = [
            'numero_despacho',
            'fecha_movimiento',
            'tipo_movimiento', 'usuario_responsable', 'motorista_asignado',
            'observacion', 'estado', 'origen', 'destino', 
            'movimiento_padre'
        ]
        widgets = {
            'numero_despacho': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678'}),
            'fecha_movimiento': NativeDateTimeInput(),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-select'}),
            'usuario_responsable': forms.Select(attrs={'class': 'form-select'}),
            'motorista_asignado': forms.Select(attrs={'class': 'form-select'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'movimiento_padre': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['movimiento_padre'].required = False
        self.fields['motorista_asignado'].required = False
        
        if self.initial.get('movimiento_padre'):
            # Es un hijo: Ocultamos numero_despacho
            self.fields['numero_despacho'].widget = forms.HiddenInput()
            self.fields['numero_despacho'].required = False
        else:
            # Es un padre: Es obligatorio
            self.fields['numero_despacho'].required = True

    def clean(self):
        cleaned_data = super().clean()
        motorista = cleaned_data.get('motorista_asignado')
        estado = cleaned_data.get('estado') 
        movimiento_padre = cleaned_data.get('movimiento_padre')

        if not motorista or estado != 'pendiente':
            return cleaned_data
        conflictos = Movimiento.objects.filter(
            motorista_asignado=motorista,
            estado='pendiente'
        )
        if self.instance.pk:
            conflictos = conflictos.exclude(pk=self.instance.pk)
        if movimiento_padre:
            conflictos = conflictos.exclude(pk=movimiento_padre.pk)
            conflictos = conflictos.exclude(movimiento_padre=movimiento_padre)

        if conflictos.exists():
            ocupado_en = conflictos.first()
            nro = ocupado_en.numero_despacho
            if not nro and ocupado_en.movimiento_padre:
                nro = f"{ocupado_en.movimiento_padre.numero_despacho} (Tramo)"
            
            raise forms.ValidationError(
                f"El motorista {motorista} ya tiene un despacho pendiente activo ({nro}). Termine ese trabajo antes de asignarle uno nuevo distinto."
            )

        return cleaned_data

    def clean_origen(self):
        origen = self.cleaned_data.get('origen')
        motorista = self.cleaned_data.get('motorista_asignado')
        movimiento_padre = self.cleaned_data.get('movimiento_padre')


        if not movimiento_padre and motorista:
            asignacion = AsignacionFarmacia.objects.filter(
                motorista=motorista,
                fechaTermino__isnull=True
            ).last()
            
            if asignacion:
                farmacia_actual = asignacion.farmacia.nombre
                if farmacia_actual.lower() not in origen.lower():
                    pass 
        
        return origen

# --- ASIGNACIONES ---
class AsignacionFarmaciaForm(forms.ModelForm):
    """Formulario para asignar una Farmacia a un Motorista."""
    class Meta:
        model = AsignacionFarmacia
        fields = ['farmacia', 'observaciones']
        widgets = {
            'farmacia': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AsignacionMotoForm(forms.ModelForm):
    """Formulario para asignar una Moto a un Motorista."""
    class Meta:
        model = AsignacionMoto
        fields = ['motorista', 'estado']
        widgets = {
            'motorista': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
class LoginForm(forms.Form):
    """Formulario simple para el inicio de sesión."""
    credencial = forms.CharField(
        label="Usuario o Correo",
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario o email', 'autocomplete': 'username'})
    )
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'})
    )