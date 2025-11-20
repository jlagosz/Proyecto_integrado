# Proyecto de Gestión "DiscoPro"

Sistema de gestión logística para la administración de farmacias, motoristas y despachos, construido con Django.

## Características Principales

Este proyecto es una aplicación web de gestión interna que permite llevar un control detallado de los activos y operaciones de una red de despachos.

* **Dashboard de Resumen:** Una vista principal con métricas clave del sistema.
* **Gestión de Entidades (CRUD):** Funcionalidad completa de Crear, Leer, Actualizar y Eliminar para:
  * Farmacias
  * Motoristas
  * Motos
* **Lógica de Asignación Avanzada:** Modelos de historial para asignar motoristas a farmacias (`AsignacionFarmacia`) y motoristas a motos (`AsignacionMoto`).
* **Seguimiento de Movimientos:** Sistema avanzado para registrar "Movimientos Padre" (la operación completa) y "Tramos Hijos" (las etapas individuales), permitiendo una logística compleja y encadenada (ej. A→B, B→C).
* **Gestión de Documentos y Mantenimiento:**
  * Subida de archivos para la licencia de conducir del motorista.
  * Gestión de la documentación de la moto (Permiso, Seguro, Revisión Técnica) con fechas de vencimiento.
  * Historial de mantenimientos por vehículo.
* **Estructura de Datos Profesional:** Modelos normalizados para datos geográficos (`Region`, `Provincia`, `Comuna`).
* **Modelos de Rol/Usuario:** Estructura de BD (`Usuario`, `Rol`) preparada para la futura gestión de operadores del sistema.

## Pila Tecnológica (Stack)

* **Backend:** Python 3.13, Django 5.2.x
* **Base de Datos:** MariaDB (MySQL)
* **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons
* **Configuración:** `python-dotenv` (para gestión de secretos), `venv` (entorno virtual).
* **Entorno de Desarrollo:** XAMPP (para Apache y MariaDB), phpMyAdmin.

## Puesta en Marcha Local

Sigue estos pasos para clonar y ejecutar el proyecto en tu máquina local.

### 1. Prerrequisitos

* Python 3.10 o superior.
* Git.
* **XAMPP** : Asegúrate de tener XAMPP instalado y los servicios de **Apache** y **MySQL** corriendo.

### 2. Clonar el Repositorio

```
# Clona este repositorio en tu máquina
git clone [https://github.com/](https://github.com/)[TU_USUARIO]/[TU_REPOSITORIO].git
cd mi_proyecto
```

### 3. Configuración del Entorno

**a. Crear y Activar el Entorno Virtual**

```
# 1. Crear el entorno virtual
python -m venv venv

# 2. Activar el entorno (Windows)
.\venv\Scripts\activate
```

**b. Instalar las Dependencias**
El archivo `requirements.txt` instala Django y todas las librerías necesarias.

```
pip install -r requirements.txt
```

**c. Configurar la Base de Datos y Secretos**

1. **Crear la Base de Datos:** Abre `http://localhost/phpmyadmin` y crea una nueva base de datos llamada `discopro_db` (asegúrate de usar el cotejamiento `utf8mb4_general_ci`).
2. **Crear el archivo `.env`:** En la raíz del proyecto (junto a `manage.py`), crea un archivo llamado `.env`.
3. **Copiar y pegar** el siguiente contenido en el archivo `.env` y llénalo con tus credenciales.
   ```
   # ¡Reemplaza esto con tu propia clave secreta de Django!
   SECRET_KEY='django-insecure-tu-clave-aqui'

   # Datos de tu base de datos XAMPP
   DB_NAME='discopro_db'
   DB_USER='root'
   DB_PASSWORD='' # (Pon tu contraseña de root de XAMPP aquí, si tienes una)
   DB_HOST='127.0.0.1'
   DB_PORT='3306'

   # Token de SonarQube (si lo usas)
   sonar.token=squ_...
   ```

### 4. Ejecutar la Aplicación

**a. Aplicar las Migraciones (Construir las tablas)**

```
python manage.py migrate
```

**b. Crear un Superusuario (Para acceder al Admin)**

```
python manage.py createsuperuser
```

**c. Iniciar el Servidor**

```
python manage.py runserver
```
