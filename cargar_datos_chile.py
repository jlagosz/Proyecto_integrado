import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')
django.setup()

from discopro.models import Region, Provincia, Comuna

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

def cargar_datos():
    print("Iniciando carga de datos geográficos...")
    
    contador_reg = 0
    contador_prov = 0
    contador_com = 0

    for nombre_region, provincias in data_chile.items():
        # Crear o recuperar Región
        region_obj, created = Region.objects.get_or_create(nombreRegion=nombre_region)
        if created:
            contador_reg += 1
            print(f" [+] Región creada: {nombre_region}")

        for nombre_provincia, comunas in provincias.items():
            # Crear o recuperar Provincia vinculada a la Región
            provincia_obj, created = Provincia.objects.get_or_create(
                nombreProvincia=nombre_provincia,
                region=region_obj
            )
            if created:
                contador_prov += 1

            for nombre_comuna in comunas:
                # Crear o recuperar Comuna vinculada a la Provincia
                comuna_obj, created = Comuna.objects.get_or_create(
                    nombreComuna=nombre_comuna,
                    provincia=provincia_obj
                )
                if created:
                    contador_com += 1
    
    print("-" * 50)
    print(f"PROCESO TERMINADO EXITOSAMENTE.")
    print(f"Regiones agregadas: {contador_reg}")
    print(f"Provincias agregadas: {contador_prov}")
    print(f"Comunas agregadas: {contador_com}")
    print("-" * 50)

if __name__ == '__main__':
    cargar_datos()