from django import forms
from .models import (
    Farmacia, Motorista, Moto, ContactoEmergencia, 
    AsignacionFarmacia, AsignacionMoto, Documentacion, DocumentacionMoto,
    Mantenimiento, TipoMovimiento, Movimiento, Usuario, Rol
)

# --- WIDGETS NATIVOS ---
class NativeDateInput(forms.DateInput):
    input_type = 'date'
    attrs = {'class': 'form-control'} 

class NativeTimeInput(forms.TimeInput):
    input_type = 'time'
    attrs = {'class': 'form-control'}

class FarmaciaForm(forms.ModelForm):
    class Meta:
        model = Farmacia
        fields = [
            'nombre', 'direccion', 'comuna', 
            'horario_apertura', 'horario_cierre', 'telefono', 
            'latitud', 'longitud'
        ]
        widgets = {
            'horario_apertura': NativeTimeInput(),
            'horario_cierre': NativeTimeInput(),
        }
class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = [
            'rut', 'pasaporte', 'nombres', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'direccion', 'comuna', 'telefono', 'correo',
            'estado',
            'licencia_conducir', 'fecha_ultimo_control', 'fecha_proximo_control'
        ]
        widgets = {
            'fecha_nacimiento': NativeDateInput(),
            'fecha_ultimo_control': NativeDateInput(),
            'fecha_proximo_control': NativeDateInput(),
        }
class MotoForm(forms.ModelForm):
    class Meta:
        model = Moto
        fields = [
            'patente', 'marca', 'modelo', 'color', 'anio', 
            'numero_chasis', 'motor'
        ]
class AsignacionFarmaciaForm(forms.ModelForm):
    class Meta:
        model = AsignacionFarmacia
        fields = ['farmacia', 'observaciones']
        widgets = {
            'farmacia': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class AsignacionMotoForm(forms.ModelForm):
    class Meta:
        model = AsignacionMoto
        fields = ['motorista', 'estado']
        widgets = {
            'motorista': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }
class ContactoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContactoEmergencia
        fields = ['nombreCompleto', 'parentesco', 'telefono']
class DocumentacionForm(forms.ModelForm):
    class Meta:
        model = Documentacion
        fields = ['nombreDocumento', 'archivo', 'fechaVencimiento']
class DocumentacionMotoForm(forms.ModelForm):
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

# --- FORMULARIOS DE MOVIMIENTO ---

class TipoMovimientoForm(forms.ModelForm):
    class Meta:
        model = TipoMovimiento
        fields = '__all__'

class MovimientoForm(forms.ModelForm):
    """
    Formulario para crear/editar un Despacho (Padre) o un Tramo (Hijo).
    """
    class Meta:
        model = Movimiento
        fields = [
            'tipo_movimiento', 'usuario_responsable', 'motorista_asignado',
            'observacion', 'estado', 'origen', 'destino', 
            'movimiento_padre'
        ]
        widgets = {
            'tipo_movimiento': forms.Select(attrs={'class': 'form-select'}),
            'usuario_responsable': forms.Select(attrs={'class': 'form-select'}),
            'motorista_asignado': forms.Select(attrs={'class': 'form-select'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'movimiento_padre': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['movimiento_padre'].required = False
        self.fields['motorista_asignado'].required = False

class UsuarioForm(forms.ModelForm):
    """
    Formulario para crear y actualizar el modelo Usuario.
    """
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Déjalo en blanco para no cambiar la contraseña."
    )
    
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Confirmar contraseña"
    )

    class Meta:
        model = Usuario
        fields = [
            'rut', 'nombres', 'apellidos', 'correo', 'telefono', 
            'estado', 'rol', 'nombreUsuario', 'contrasena', 'confirmar_contrasena'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'nombreUsuario': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['contrasena'].required = True
            self.fields['confirmar_contrasena'].required = True
            self.fields['contrasena'].help_text = "Ingresa una contraseña segura."

    def clean(self):
        """
        Valida que las dos contraseñas coincidan.
        """
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar_contrasena = cleaned_data.get("confirmar_contrasena")

        if contrasena or (not self.instance.pk):
            if contrasena != confirmar_contrasena:
                raise forms.ValidationError(
                    "Las contraseñas no coinciden."
                )
        return cleaned_data

    def save(self, commit=True):
        """
        Sobrescribe el método save para hashear la contraseña.
        """
        usuario = super().save(commit=False)
        contrasena = self.cleaned_data.get("contrasena")

        if contrasena:
            usuario.set_password(contrasena) 

        if commit:
            usuario.save()
        return usuario