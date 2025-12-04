import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')
django.setup()

from discopro.models import (
    Region, Provincia, Comuna,
    Farmacia, Motorista, Moto, ContactoEmergencia,
    AsignacionFarmacia, AsignacionMoto, Documentacion, DocumentacionMoto,
    Mantenimiento, TipoMovimiento, Movimiento,
    Usuario
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
            print("ERROR: Faltan datos base.")

            print("Debes verificar:")
            print("1) Haber cargado las regiones, provincias y comunas.")
            print("2) Haber creado al menos un TipoMovimiento.")
            print("3) Tener al menos un superusuario.")
            return None, None, None, None

        return comuna_base, region_base, tipo_mov_base, usuario_base

    except Exception as e:
        print(f"ERROR al obtener dependencias: {e}")
        return None, None, None, None


# ------------------------------------------------------
# 2. FUNCIÓN PRINCIPAL DE CREACIÓN DE OBJETOS
# ------------------------------------------------------
def crear_objetos_prueba():
    print("--------------------------------------------------")
    print(" CREANDO DATOS DE PRUEBA (2 por módulo) ")
    print("--------------------------------------------------")

    comuna, region, tipo_movimiento, usuario = get_dependencies()
    if not comuna:
        return

    objetos_creados = {
        'Farmacia': 0,
        'Motorista': 0,
        'Moto': 0,
        'AsignaciónFarmacia': 0,
        'Movimiento': 0
    }

    # ------------------------------------------------------
    # 1. FARMACIAS
    # ------------------------------------------------------
    farmacias = []
    for i in range(1, 3):
        f, created = Farmacia.objects.get_or_create(
            nombre=f"Farmacia Test {i}",
            comuna=comuna,
            defaults={
                'direccion': f"Calle Falsa {100 + i}",
                'telefono': f'+569000000{i}',
                'horario_apertura': '09:00',
                'horario_cierre': '21:00'
            }
        )
        farmacias.append(f)
        if created:
            objetos_creados['Farmacia'] += 1

    print(f"Farmacias creadas: {objetos_creados['Farmacia']}")

    # ------------------------------------------------------
    # 2. MOTORISTAS
    # ------------------------------------------------------
    motoristas = []
    for i in range(1, 3):
        m, created = Motorista.objects.get_or_create(
            rut=f'11.111.11{i}-K',
            comuna=comuna,
            defaults={
                'codigo': f'{100 + i}',
                'nombres': f"Juan Test {i}",
                'apellido_paterno': "Pérez",
                'direccion': f'Av Test {200 + i}',
                'telefono': f'+569111111{i}',
                'estado': 'activo',
                'fecha_nacimiento': '1990-01-01'
            }
        )
        motoristas.append(m)
        if created:
            objetos_creados['Motorista'] += 1

    print(f"Motoristas creados: {objetos_creados['Motorista']}")

    # ------------------------------------------------------
    # 3. MOTOS
    # ------------------------------------------------------
    motos = []
    if motoristas:
        propietario = motoristas[0]
        for i in range(1, 3):
            moto, created = Moto.objects.get_or_create(
                patente=f'ABCD{10 + i}',
                defaults={
                    'marca': f"Marca {i}",
                    'modelo': "Modelo X",
                    'color': 'Rojo',
                    'anio': 2020 + i,
                    'propietario': propietario
                }
            )
            motos.append(moto)
            if created:
                objetos_creados['Moto'] += 1

    print(f"Motos creadas: {objetos_creados['Moto']}")

    # ------------------------------------------------------
    # 4. ASIGNACIÓN DE MOTORISTAS A FARMACIA
    # ------------------------------------------------------
    if motoristas and farmacias:
        for motorista in motoristas:
            asignacion, created = AsignacionFarmacia.objects.get_or_create(
                motorista=motorista,
                farmacia=farmacias[0],
                defaults={'observaciones': 'Asignación automática de prueba'}
            )
            if created:
                objetos_creados['AsignaciónFarmacia'] += 1

    print(f"Asignaciones creadas: {objetos_creados['AsignaciónFarmacia']}")

    # ------------------------------------------------------
    # 5. MOVIMIENTOS
    # ------------------------------------------------------
    if motoristas and tipo_movimiento:
        for i in range(1, 3):
            mov, created = Movimiento.objects.get_or_create(
                numero_despacho=f'DSP{1000 + i}',
                tipo_movimiento=tipo_movimiento,
                usuario_responsable=usuario,
                motorista_asignado=motoristas[0],
                defaults={
                    'estado': 'pendiente',
                    'origen': farmacias[0].nombre,
                    'destino': comuna.nombreComuna
                }
            )
            if created:
                objetos_creados['Movimiento'] += 1

    print(f" Movimientos creados: {objetos_creados['Movimiento']}")

    # ------------------------------------------------------
    # RESUMEN FINAL
    # ------------------------------------------------------
    print("\n==================================================")
    print(" DATOS DE PRUEBA CREADOS CORRECTAMENTE ")
    print("==================================================")
    for k, v in objetos_creados.items():
        print(f" - {k}: {v}")
    print("==================================================")


# Ejecutar script
if __name__ == '__main__':
    crear_objetos_prueba()
