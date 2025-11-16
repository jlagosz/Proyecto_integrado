from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password

# ---  Modelos Geográficos ---
class Region(models.Model):
    idRegion = models.AutoField(primary_key=True)
    nombreRegion = models.CharField(max_length=100)
    def __str__(self):
        return self.nombreRegion
    def get_absolute_url(self): 
        return reverse('detalle_region', kwargs={'pk': self.pk})

class Provincia(models.Model):
    idProvincia = models.AutoField(primary_key=True)
    nombreProvincia = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    def __str__(self):
        return self.nombreProvincia
    def get_absolute_url(self): 
        return reverse('detalle_provincia', kwargs={'pk': self.pk})

class Comuna(models.Model):
    idComuna = models.AutoField(primary_key=True)
    nombreComuna = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    def __str__(self):
        return self.nombreComuna
    def get_absolute_url(self): 
        return reverse('detalle_comuna', kwargs={'pk': self.pk})

# --- Modelos de Usuario y Rol ---
class Rol(models.Model):
    idRol = models.AutoField(primary_key=True)
    nombreRol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombreRol

class Usuario(models.Model):
    ESTADO_ACTIVO = 'Activo'
    ESTADO_INACTIVO = 'Inactivo'
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]
    idUsuario = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO
    )
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)

    # --- CAMPOS DE LOGIN ---
    nombreUsuario = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Usuario")
    contrasena = models.CharField(max_length=128, verbose_name="Contraseña")
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    # --- MÉTODOS DE LOGIN ---
    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)

# --- Modelos Principales ---
class Farmacia(models.Model):
    codigo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, verbose_name="Nombre de Farmacia")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT)
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    def __str__(self):
        return self.nombre
    def get_absolute_url(self): 
        return reverse('detalle_farmacia', kwargs={'pk': self.pk})

class Motorista(models.Model):
    ESTADO_ACTIVO = 'activo'
    ESTADO_INACTIVO = 'inactivo'
    ESTADO_LICENCIA = 'licencia'
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
        (ESTADO_LICENCIA, 'Con Licencia Médica'),
    ]
    codigo = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True)
    pasaporte = models.CharField(max_length=20, null=True, blank=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=200)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    licencia_conducir = models.FileField(upload_to="licencias/", null=True, blank=True)
    fecha_ultimo_control = models.DateField(null=True, blank=True)
    fecha_proximo_control = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado"
    )
    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno}"
    def get_absolute_url(self): 
        return reverse('detalle_motorista', kwargs={'pk': self.pk})

class Moto(models.Model):
    patente = models.CharField(max_length=15, primary_key=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    anio = models.IntegerField(verbose_name="Año")
    numero_chasis = models.CharField(max_length=50, blank=True, null=True)
    motor = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"
    def get_absolute_url(self): 
        return reverse('detalle_moto', kwargs={'pk': self.pk})

# --- Modelos de Relación ---

class ContactoEmergencia(models.Model):
    idContacto = models.AutoField(primary_key=True)
    nombreCompleto = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, related_name="contactos_emergencia")
    def __str__(self):
        return self.nombreCompleto

class Documentacion(models.Model):
    idDocumentacion = models.AutoField(primary_key=True)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, related_name="documentos")
    nombreDocumento = models.CharField(max_length=100)
    archivo = models.FileField(upload_to="documentos_motorista/")
    fechaVencimiento = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.nombreDocumento} - {self.motorista}"

class DocumentacionMoto(models.Model):
    id = models.AutoField(primary_key=True) 
    moto = models.OneToOneField(Moto, on_delete=models.CASCADE, related_name='documentacion') 
    anio = models.IntegerField(default=timezone.now().year, verbose_name="Año del Permiso de Circulación")

    permiso_circulacion_file = models.FileField(upload_to="documentos_moto/permiso_circulacion/", null=True, blank=True, verbose_name="Permiso de Circulación (Archivo)")
    permiso_circulacion_vencimiento = models.DateField(null=True, blank=True, verbose_name="Vencimiento Permiso de Circulación")

    seguro_obligatorio_file = models.FileField(upload_to="documentos_moto/seguro_obligatorio/", null=True, blank=True, verbose_name="Seguro Obligatorio (Archivo)")
    seguro_obligatorio_vencimiento = models.DateField(null=True, blank=True, verbose_name="Vencimiento Seguro Obligatorio")

    revision_tecnica_file = models.FileField(upload_to="documentos_moto/revision_tecnica/", null=True, blank=True, verbose_name="Revisión Técnica (Archivo)")
    revision_tecnica_vencimiento = models.DateField(null=True, blank=True, verbose_name="Vencimiento Revisión Técnica")
    
    def __str__(self): return f"Documentación de {self.moto.patente} ({self.anio})"

    def is_permiso_vigente(self):
        return self.permiso_circulacion_vencimiento and self.permiso_circulacion_vencimiento >= timezone.localdate()

    def is_seguro_vigente(self):
        return self.seguro_obligatorio_vencimiento and self.seguro_obligatorio_vencimiento >= timezone.localdate()

    def is_revision_vigente(self):
        return self.revision_tecnica_vencimiento and self.revision_tecnica_vencimiento >= timezone.localdate()

class Mantenimiento(models.Model):
    moto = models.ForeignKey(Moto, on_delete=models.CASCADE, related_name='mantenimientos')
    fecha_mantenimiento = models.DateField(default=timezone.now, verbose_name="Fecha de Mantenimiento")
    descripcion = models.TextField(verbose_name="Descripción del Mantenimiento")
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Costo")
    taller = models.CharField(max_length=100, blank=True, null=True, verbose_name="Taller")
    kilometraje = models.IntegerField(null=True, blank=True, verbose_name="Kilometraje")
    factura = models.FileField(upload_to="mantenimientos/", null=True, blank=True, verbose_name="Factura/Comprobante")

    def __str__(self): return f"Mantenimiento {self.moto.patente} - {self.fecha_mantenimiento.strftime('%d-%m-%Y')}"
    def get_absolute_url(self): return reverse('detalle_moto', kwargs={'pk': self.moto.patente})

class AsignacionFarmacia(models.Model):
    idAsignacionFarmacia = models.AutoField(primary_key=True)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE)
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    fechaAsignacion = models.DateField(default=timezone.now)
    observaciones = models.TextField(blank=True, null=True)
    fechaTermino = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.motorista} asignado a {self.farmacia}"

class AsignacionMoto(models.Model):
    idAsignacionMoto = models.AutoField(primary_key=True)
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True)
    moto = models.ForeignKey(Moto, on_delete=models.CASCADE)
    fechaAsignacion = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=50, default="Asignada") # Ej: Asignada, En Taller, etc.
    fechaTermino = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.moto} asignada a {self.motorista}"

# --- 5. ¡NUEVOS MODELOS DE MOVIMIENTOS! ---

class TipoMovimiento(models.Model):
    """
    Almacena los tipos de movimientos (tramos) que se pueden registrar.
    Ej: Directo, Receta médica, Fallido, Reenvió, Traspaso.
    """
    idTipoMovimiento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Tipo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

class Movimiento(models.Model):
    """
    Implementa la lógica de "movimientos anidados" (padre/hijo).
    Un "Movimiento Padre" (con 'movimiento_padre' en Nulo) es un "Despacho".
    Un "Movimiento Hijo" (con 'movimiento_padre' apuntando al padre) es un "Tramo".
    """
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('anulado', 'Anulado'),
    )

    id_movimiento = models.AutoField(primary_key=True, verbose_name="Identificador único")
    
    tipo_movimiento = models.ForeignKey(
        TipoMovimiento, 
        on_delete=models.PROTECT, 
        verbose_name="Tipo de Movimiento"
    )
    
    fecha_movimiento = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Fecha y hora del movimiento"
    )
    
    usuario_responsable = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        verbose_name="Usuario Responsable (Operador)"
    )
    
    observacion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción / Observación"
    )
    
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente', 
        verbose_name="Estado"
    )
    
    origen = models.CharField(
        max_length=255, 
        verbose_name="Origen (Bodega/sector que entrega)"
    )
    
    destino = models.CharField(
        max_length=255, 
        verbose_name="Destino (Bodega/sector que recibe)"
    )
    
    motorista_asignado = models.ForeignKey(
        Motorista, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Motorista Asignado"
    )
    
    movimiento_padre = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='tramos_hijos', 
        verbose_name="Movimiento Padre (Despacho)"
    )

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"

    def __str__(self):
        if self.movimiento_padre:
            return f"Tramo (Hijo) {self.id_movimiento} del Despacho {self.movimiento_padre.id_movimiento}"
        else:
            return f"Despacho (Padre) {self.id_movimiento}: {self.origen} -> {self.destino}"

    def get_absolute_url(self):
        if self.movimiento_padre:
            return reverse('movimiento_detalle', kwargs={'pk': self.movimiento_padre.pk})
        return reverse('movimiento_detalle', kwargs={'pk': self.pk})