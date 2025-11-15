from django import forms
from .models import (
    Farmacia, Motorista, Moto, ContactoEmergencia, 
    AsignacionFarmacia, AsignacionMoto, Documentacion, DocumentacionMoto,
    Mantenimiento, TipoMovimiento, Movimiento
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