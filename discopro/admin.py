from django.contrib import admin
from . import models

# --- Modelos Geográficos ---
@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    """Administración de Regiones geográficas."""
    list_display = ('idRegion', 'nombreRegion')

@admin.register(models.Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    """Administración de Provincias."""
    list_display = ('nombreProvincia', 'region')
    list_filter = ('region',)

@admin.register(models.Comuna)
class ComunaAdmin(admin.ModelAdmin):
    """Administración de Comunas con filtrado por región y provincia."""
    list_display = ('nombreComuna', 'provincia', 'get_region')
    list_filter = ('provincia__region', 'provincia')
    search_fields = ('nombreComuna',)

    @admin.display(description='Región')
    def get_region(self, obj):
        return obj.provincia.region

# --- Modelos de Usuario/Rol ---
@admin.register(models.Rol)
class RolAdmin(admin.ModelAdmin):
    """Gestión de Roles de usuario (Operador, Gerente, etc.)."""
    list_display = ('idRol', 'nombreRol')

@admin.register(models.Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Gestión de Usuarios del sistema."""
    list_display = ('nombres', 'apellidos', 'rut', 'correo', 'rol', 'estado')
    list_filter = ('rol', 'estado')
    search_fields = ('nombres', 'apellidos', 'rut')

# --- Modelos Principales ---
@admin.register(models.Farmacia)
class FarmaciaAdmin(admin.ModelAdmin):
    """Gestión de Farmacias."""
    list_display = ('nombre', 'direccion', 'comuna')
    list_filter = ('comuna__provincia__region',)
    search_fields = ('nombre', 'comuna__nombreComuna')

@admin.register(models.Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    """Gestión de Motoristas."""
    list_display = ('nombres', 'apellido_paterno', 'rut', 'comuna')
    search_fields = ('nombres', 'rut')

@admin.register(models.Moto)
class MotoAdmin(admin.ModelAdmin):
    """Gestión de la flota de Motos."""
    list_display = ('patente', 'marca', 'modelo', 'anio')
    search_fields = ('patente', 'marca')

# --- Modelos de Relación ---
admin.site.register(models.ContactoEmergencia)
admin.site.register(models.Documentacion)
admin.site.register(models.DocumentacionMoto)

@admin.register(models.AsignacionFarmacia)
class AsignacionFarmaciaAdmin(admin.ModelAdmin):
    """Historial de asignaciones Motorista -> Farmacia."""
    list_display = ('motorista', 'farmacia', 'fechaAsignacion')
    list_filter = ('fechaAsignacion',)

@admin.register(models.AsignacionMoto)
class AsignacionMotoAdmin(admin.ModelAdmin):
    """Historial de asignaciones Moto -> Motorista."""
    list_display = ('moto', 'motorista', 'fechaAsignacion', 'estado')
    list_filter = ('estado', 'fechaAsignacion')

@admin.register(models.Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    """Registro de mantenimientos de vehículos."""
    list_display = ('moto', 'fecha_mantenimiento', 'descripcion', 'taller', 'costo')
    list_filter = ('fecha_mantenimiento', 'moto__marca')
    search_fields = ('moto__patente', 'descripcion', 'taller')

@admin.register(models.TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
    """Configuración de tipos de movimientos logísticos."""
    list_display = ('idTipoMovimiento', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(models.Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    """Gestión centralizada de Despachos y Tramos."""
    list_display = ('numero_despacho', 'id_movimiento', 'get_tipo_movimiento', 'estado', 'fecha_movimiento', 'usuario_responsable', 'motorista_asignado', 'get_despacho_padre')
    list_filter = ('estado', 'tipo_movimiento', 'fecha_movimiento')
    search_fields = ('id_movimiento', 'observacion', 'origen', 'destino')
    list_per_page = 20

    @admin.display(description='Tipo')
    def get_tipo_movimiento(self, obj):
        return obj.tipo_movimiento.nombre

    @admin.display(description='Despacho Padre')
    def get_despacho_padre(self, obj):
        return obj.movimiento_padre_id