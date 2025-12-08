from django.contrib import admin
from django.urls import path, include  # <--- 1. AGREGAR 'include' AQUÍ
from discopro import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- RUTAS DE AUTENTICACIÓN Y PASSWORD RESET ---
    path('accounts/', include('django.contrib.auth.urls')), 

    # --- VISTA LOGIN PROPIA ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- VISTA PRINCIPAL (DASHBOARD) ---
    path('', views.index, name='index'), 

    # --- CRUD USUARIOS ---
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_lista'),
    path('usuarios/crear/', views.UsuarioCreateView.as_view(), name='usuario_crear'),
    path('usuarios/editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='usuario_editar'),
    path('usuarios/eliminar/<int:pk>/', views.UsuarioDeleteView.as_view(), name='usuario_eliminar'),
    
    # --- CONFIG USUARIOS --
    path('mi-cuenta/', views.MiCuentaView.as_view(), name='mi_cuenta'),
    path('configuracion/', views.ConfiguracionView.as_view(), name='configuracion'),
    
    # --- CRUD FARMACIAS ---
    path('farmacias/', views.FarmaciaListView.as_view(), name='farmacia_lista'), 
    path('farmacias/crear/', views.FarmaciaCreateView.as_view(), name='farmacia_crear'),
    path('farmacias/editar/<int:pk>/', views.FarmaciaUpdateView.as_view(), name='farmacia_editar'),
    path('farmacias/eliminar/<int:pk>/', views.FarmaciaDeleteView.as_view(), name='farmacia_eliminar'), 
    path('farmacias/detalle/<int:pk>/', views.FarmaciaDetailView.as_view(), name='farmacia_detalle'),
    
    # --- CRUD MOTORISTAS ---
    path('motoristas/', views.MotoristaListView.as_view(), name='motorista_lista'),
    path('motoristas/crear/', views.MotoristaCreateView.as_view(), name='motorista_crear'),
    path('motoristas/detalle/<int:pk>/', views.MotoristaDetailView.as_view(), name='motorista_detalle'),
    path('motoristas/editar/<int:pk>/', views.MotoristaUpdateView.as_view(), name='motorista_editar'),
    path('motoristas/eliminar/<int:pk>/', views.MotoristaDeleteView.as_view(), name='motorista_eliminar'),
    
    # Contactos (Sub-recurso de motorista)
    path('motorista/<int:motorista_pk>/crear-contacto/', views.ContactoEmergenciaCreateView.as_view(), name='contacto_crear'),
    path('contacto/eliminar/<int:pk>/', views.ContactoEmergenciaDeleteView.as_view(), name='contacto_eliminar'),
    
    # --- CRUD MOTOS ---
    path('motos/', views.MotoListView.as_view(), name='moto_lista'),
    path('motos/crear/', views.MotoCreateView.as_view(), name='moto_crear'),
    path('motos/detalle/<str:pk>/', views.MotoDetailView.as_view(), name='moto_detalle'),
    path('motos/editar/<str:pk>/', views.MotoUpdateView.as_view(), name='moto_editar'),
    path('motos/eliminar/<str:pk>/', views.MotoDeleteView.as_view(), name='moto_eliminar'),

     # --- DOCUMENTOS Y MANTENIMIENTO ---
    path('moto/<str:pk>/documentacion/', views.DocumentacionMotoUpdateView.as_view(), name='moto_documentacion'),  
    path('moto/<str:pk>/mantenimiento/crear/', views.MantenimientoCreateView.as_view(), name='mantenimiento_crear'),

    # --- CRUD MOVIMIENTOS ---
    path('movimientos/', views.MovimientoListView.as_view(), name='movimiento_lista'),
    path('movimientos/crear/', views.MovimientoCreateView.as_view(), name='movimiento_crear'),
    path('movimientos/detalle/<int:pk>/', views.MovimientoDetailView.as_view(), name='movimiento_detalle'),
    path('movimientos/editar/<int:pk>/', views.MovimientoUpdateView.as_view(), name='movimiento_editar'),
    path('movimientos/eliminar/<int:pk>/', views.MovimientoDeleteView.as_view(), name='movimiento_eliminar'),
    
    # --- CRUD TRAMOS ---
    path('movimientos/detalle/<int:padre_pk>/crear-tramo/', views.TramoCreateView.as_view(), name='tramo_crear'),
    path('tramos/editar/<int:pk>/', views.TramoUpdateView.as_view(), name='tramo_editar'),
    path('tramos/eliminar/<int:pk>/', views.TramoDeleteView.as_view(), name='tramo_eliminar'),
    
    # --- VISTAS DE ASIGNACIÓN ---
    path('motorista/<int:motorista_pk>/asignar-farmacia/', views.AsignacionFarmaciaCreateView.as_view(), name='asignacion_farmacia_crear'),
    path('moto/<str:moto_pk>/asignar-motorista/', views.AsignacionMotoCreateView.as_view(), name='asignacion_moto_crear'),

    # --- REPORTES ---
    path('movimientos/reportes/', views.ReporteMovimientosView.as_view(), name='reporte_movimientos'),
    path('movimientos/reportes/pdf/', views.ExportarReportePDFView.as_view(), name='reporte_pdf'),

    # --- AJAX SELECTS DEPENDIENTES ---
    path('ajax/load-provincias/', views.load_provincias, name='ajax_load_provincias'),
    path('ajax/load-comunas/', views.load_comunas, name='ajax_load_comunas'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Corrección menor: es MEDIA_ROOT