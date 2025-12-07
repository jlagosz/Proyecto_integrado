import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')
django.setup()

from discopro.models import (
    Region, Provincia, Comuna,
    Farmacia, Motorista, Moto,
    AsignacionFarmacia, AsignacionMoto, 
    TipoMovimiento, Movimiento, Usuario
)

# ------------------------------------------------------
# 1. OBTENER DEPENDENCIAS BASE
# ------------------------------------------------------
def get_dependencies():
    """Retorna los objetos mínimos necesarios para crear datos."""
    try:
        comuna_base = Comuna.objects.first()
        region_base = Region.objects.first()
        tipo_mov_base = TipoMovimiento.objects.first()
        usuario_base = Usuario.objects.filter(is_superuser=True).first()

        if not comuna_base or not tipo_mov_base or not usuario_base:
            print("ERROR: Faltan datos base (Comuna, TipoMovimiento o Superuser).")
            return None, None, None, None

        return comuna_base, region_base, tipo_mov_base, usuario_base

    except Exception as e:
        print(f"ERROR al obtener dependencias: {e}")
        return None, None, None, None


# ------------------------------------------------------
# 2. FUNCIÓN PRINCIPAL
# ------------------------------------------------------
def crear_objetos_prueba():
    print("--------------------------------------------------")
    print(" CREANDO DATOS DE PRUEBA MASIVOS (21 registros) ")
    print("--------------------------------------------------")

    comuna, region, tipo_movimiento, usuario = get_dependencies()
    if not comuna:
        return

    objetos_creados = {
        'Farmacia': 0, 'Motorista': 0, 'Moto': 0,
        'AsignaciónFarmacia': 0, 'Movimiento': 0
    }


    CANTIDAD = 22 

    # --- 1. FARMACIAS ---
    print(">>> Creando Farmacias...")
    farmacias = []
    for i in range(1, CANTIDAD):
        f, created = Farmacia.objects.get_or_create(
            nombre=f"Farmacia Test {i}",
            comuna=comuna,
            defaults={
                'direccion': f"Calle Falsa {100 + i}",
                'telefono': f'+569000000{i}',
                'horario_apertura': '09:00', 'horario_cierre': '21:00'
            }
        )
        farmacias.append(f)
        if created: objetos_creados['Farmacia'] += 1

    # ------------------------------------------------------
    # 2. MOTORISTAS
    # ------------------------------------------------------
    print(">>> Creando Motoristas...")
    motoristas = []
    for i in range(1, CANTIDAD):
        # Generamos un RUT ficticio que cambie con i
        rut_ficticio = f'11.111.{i:03d}-K' 
        
        m, created = Motorista.objects.get_or_create(
            rut=rut_ficticio,
            defaults={
                'nombres': f"Motorista Test {i}",
                'apellido_paterno': "Pérez",
                'apellido_materno': "Soto",
                'direccion': f'Av Test {200 + i}',
                'comuna': comuna,
                'telefono': f'+569111111{i}',
                'correo': f'motorista{i}@test.com',
                'estado': 'activo',
                'fecha_nacimiento': '1990-01-01'
            }
        )
        motoristas.append(m)
        if created:
            objetos_creados['Motorista'] += 1

    # --- 3. MOTOS ---
    print(">>> Creando Motos...")
    motos = []
    for i in range(1, CANTIDAD):
        moto, created = Moto.objects.get_or_create(
            patente=f'XX{i:02d}YY', 
            defaults={
                'marca': f"MarcaGen {i}", 'modelo': "Modelo X",
                'color': 'Rojo', 'anio': 2020 + (i % 5),
                'propietario': 'Empresa'
            }
        )
        motos.append(moto)
        if created: objetos_creados['Moto'] += 1

    # --- 4. ASIGNACIONES (Motorista -> Farmacia) ---
    print(">>> Asignando Motoristas a Farmacias...")
    if motoristas and farmacias:
        for index, motorista in enumerate(motoristas):
            # Rotamos farmacias para que no todas sean la 1
            farmacia_destino = farmacias[index % len(farmacias)]
            
            asignacion, created = AsignacionFarmacia.objects.get_or_create(
                motorista=motorista,
                farmacia=farmacia_destino,
                defaults={'observaciones': 'Carga inicial automática'}
            )
            if created: objetos_creados['AsignaciónFarmacia'] += 1

    # --- 5. MOVIMIENTOS (Aquí está el cambio clave) ---
    print(">>> Creando Movimientos (Rotando Motoristas)...")
    if motoristas and tipo_movimiento:
        for i in range(1, CANTIDAD):
            indice_motorista = (i - 1) % len(motoristas)
            moto_asignado = motoristas[indice_motorista]
            farmacia_origen = farmacias[(i - 1) % len(farmacias)]

            mov, created = Movimiento.objects.get_or_create(
                numero_despacho=f'DSP-{1000 + i}',
                defaults={
                    'tipo_movimiento': tipo_movimiento,
                    'usuario_responsable': usuario,
                    'motorista_asignado': moto_asignado,
                    'estado': 'pendiente',
                    'origen': farmacia_origen.nombre,
                    'destino': f"Dirección Cliente {i}, {comuna.nombreComuna}"
                }
            )
            if created:
                if i > 15: 
                    mov.estado = 'anulado'
                    mov.save()
                elif i > 8: 
                    mov.estado = 'completado'
                    mov.save()

                objetos_creados['Movimiento'] += 1

    # ------------------------------------------------------
    # RESUMEN FINAL
    # ------------------------------------------------------
    print("\n==================================================")
    print(" CARGA MASIVA COMPLETADA ")
    print("==================================================")
    for k, v in objetos_creados.items():
        print(f" - {k}: {v} nuevos.")
    print("==================================================")

if __name__ == '__main__':
    crear_objetos_prueba()