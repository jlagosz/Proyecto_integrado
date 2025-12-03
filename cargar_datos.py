import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')
django.setup()


from discopro.models import Region, Provincia, Comuna, TipoMovimiento

# --- DATOS DE CHILE (Estructura: Región -> Provincias -> Comunas) ---
data_chile = {
    "Región de Arica y Parinacota": {
        "Arica": ["Arica", "Camarones"],
        "Parinacota": ["Putre", "General Lagos"]
    },
    "Región de Magallanes y de la Antártica Chilena": {
        "Magallanes": ["Punta Arenas", "Laguna Blanca", "Río Verde", "San Gregorio"],
        "Antártica Chilena": ["Cabo de Hornos", "Antártica"],
        "Tierra del Fuego": ["Porvenir", "Primavera", "Timaukel"],
        "Última Esperanza": ["Natales", "Torres del Paine"]
    },
    "Región Metropolitana de Santiago": {
        "Santiago": ["Santiago", "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "Ñuñoa", "Pedro Aguirre Cerda", "Peñalolén", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Joaquín", "San Miguel", "San Ramón", "Vitacura"],
        "Cordillera": ["Puente Alto", "Pirque", "San José de Maipo"],
        "Chacabuco": ["Colina", "Lampa", "Tiltil"],
        "Maipo": ["San Bernardo", "Buin", "Calera de Tango", "Paine"],
        "Melipilla": ["Melipilla", "Alhué", "Curacaví", "María Pinto", "San Pedro"],
        "Talagante": ["Talagante", "El Monte", "Isla de Maipo", "Padre Hurtado", "Peñaflor"]
    },
    "Región de Valparaíso": {
        "Valparaíso": ["Valparaíso", "Casablanca", "Concón", "Juan Fernández", "Puchuncaví", "Quintero", "Viña del Mar"],
        "Isla de Pascua": ["Isla de Pascua"],
        "Los Andes": ["Los Andes", "Calle Larga", "Rinconada", "San Esteban"],
        "Marga Marga": ["Limache", "Olmué", "Quilpué", "Villa Alemana"],
        "Petorca": ["La Ligua", "Cabildo", "Papudo", "Petorca", "Zapallar"],
        "Quillota": ["Quillota", "Calera", "Hijuelas", "La Cruz", "Nogales"],
        "San Antonio": ["San Antonio", "Algarrobo", "Cartagena", "El Quisco", "El Tabo", "Santo Domingo"],
        "San Felipe de Aconcagua": ["San Felipe", "Catemu", "Llaillay", "Panquehue", "Putaendo", "Santa María"]
    },
    "Región de Coquimbo": {
        "Elqui": ["La Serena", "Coquimbo", "Andacollo", "La Higuera", "Paihuano", "Vicuña"],
        "Choapa": ["Illapel", "Canela", "Los Vilos", "Salamanca"],
        "Limarí": ["Ovalle", "Combarbalá", "Monte Patria", "Punitaqui", "Río Hurtado"]
    },
    "Región del Biobío": {
        "Concepción": ["Concepción", "Coronel", "Chiguayante", "Florida", "Hualqui", "Lota", "Penco", "San Pedro de la Paz", "Santa Juana", "Talcahuano", "Tomé", "Hualpén"],
        "Arauco": ["Lebu", "Arauco", "Cañete", "Contulmo", "Curanilahue", "Los Álamos", "Tirúa"],
        "Biobío": ["Los Ángeles", "Antuco", "Cabrero", "Laja", "Mulchén", "Nacimiento", "Negrete", "Quilaco", "Quilleco", "San Rosendo", "Santa Bárbara", "Tucapel", "Yumbel", "Alto Biobío"]
    }
}

# --- DATOS DE TIPOS DE MOVIMIENTO ---
data_tipos_movimiento = [
    {
        "nombre": "Directo", 
        "descripcion": "Motorista va desde farmacia hasta el destino de entrega"
    },
    {
        "nombre": "Receta médica", 
        "descripcion": "Se programa una visita antes para recepcionar la receta medica"
    },
    {
        "nombre": "Fallido", 
        "descripcion": "Por razones externas no se pudo concretar la entrega, se debe reasignar otro motorista"
    },
    {
        "nombre": "Reenvío", 
        "descripcion": "Ante entrega errónea respecto al destinatario se vuelve a realizar el envío de los productos"
    },
    {
        "nombre": "Traspaso", 
        "descripcion": "Se le ordena al motorista ir a buscar a otro local el pedido por falta de stock"
    }
]

def cargar_datos():
    print("--------------------------------------------------")
    print("Iniciando script de carga masiva...")
    print("--------------------------------------------------")
    
    # --- CARGA GEOGRÁFICA ---
    print(">>> Cargando Regiones, Provincias y Comunas...")
    contador_reg = 0
    contador_prov = 0
    contador_com = 0

    for nombre_region, provincias in data_chile.items():
        region_obj, created = Region.objects.get_or_create(nombreRegion=nombre_region)
        if created:
            contador_reg += 1

        for nombre_provincia, comunas in provincias.items():
            provincia_obj, created = Provincia.objects.get_or_create(
                nombreProvincia=nombre_provincia,
                region=region_obj
            )
            if created:
                contador_prov += 1

            for nombre_comuna in comunas:
                comuna_obj, created = Comuna.objects.get_or_create(
                    nombreComuna=nombre_comuna,
                    provincia=provincia_obj
                )
                if created:
                    contador_com += 1
    
    # --- CARGA TIPOS DE MOVIMIENTO ---
    print(">>> Cargando Tipos de Movimiento Logístico...")
    contador_tipos = 0
    
    for item in data_tipos_movimiento:
        tipo_obj, created = TipoMovimiento.objects.get_or_create(
            nombre=item["nombre"],
            defaults={"descripcion": item["descripcion"]} 
        )
        if created:
            contador_tipos += 1
            print(f" [+] Tipo creado: {item['nombre']}")
        else:
            print(f" [.] Tipo ya existente: {item['nombre']}")

    print("\n" + "=" * 50)
    print(f"RESUMEN DE CARGA")
    print("=" * 50)
    print(f"Regiones nuevas: {contador_reg}")
    print(f"Provincias nuevas: {contador_prov}")
    print(f"Comunas nuevas:    {contador_com}")
    print(f"Tipos Movimiento:  {contador_tipos}")
    print("=" * 50)

if __name__ == '__main__':
    cargar_datos()