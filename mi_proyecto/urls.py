from django.contrib import admin
from django.urls import path
from discopro import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- VISTA PRINCIPAL (DASHBOARD) ---
    path('', views.index, name='index'), 

    # --- CRUD FARMACIAS ---
    path('farmacias/', views.FarmaciaListView.as_view(), name='farmacia_lista'), 
    path('farmacias/crear/', views.FarmaciaCreateView.as_view(), name='farmacia_crear'),
    path('farmacias/editar/<int:pk>/', views.FarmaciaUpdateView.as_view(), name='farmacia_modificar'),
    path('farmacias/eliminar/<int:pk>/', views.FarmaciaDeleteView.as_view(), name='farmacia_eliminar'), 
    path('farmacias/detalle/<int:pk>/', views.FarmaciaDetailView.as_view(), name='detalle_farmacia'),
    
    # --- CRUD MOTORISTAS ---
    path('motoristas/', views.MotoristaListView.as_view(), name='motorista_lista'),
    path('motoristas/crear/', views.MotoristaCreateView.as_view(), name='agregar_motorista'),
    path('motoristas/detalle/<int:pk>/', views.MotoristaDetailView.as_view(), name='detalle_motorista'),
    path('motoristas/editar/<int:pk>/', views.MotoristaUpdateView.as_view(), name='motorista_modificar'),
    path('motoristas/eliminar/<int:pk>/', views.MotoristaDeleteView.as_view(), name='motorista_eliminar'),
    path('motorista/<int:motorista_pk>/crear-contacto/', 
         views.ContactoEmergenciaCreateView.as_view(), 
         name='crear_contacto_emergencia'),
    
    # --- CRUD MOTOS ---
    path('motos/', views.MotoListView.as_view(), name='moto_lista'),
    path('motos/crear/', views.MotoCreateView.as_view(), name='moto_crear'),
    path('motos/detalle/<str:pk>/', views.MotoDetailView.as_view(), name='detalle_moto'),
    path('motos/editar/<str:pk>/', views.MotoUpdateView.as_view(), name='moto_modificar'),
    path('motos/eliminar/<str:pk>/', views.MotoDeleteView.as_view(), name='moto_eliminar'),

     # --- DOCUMENTOS MOTOS ---
    path('moto/<str:pk>/documentacion/', views.DocumentacionMotoUpdateView.as_view(), name='gestionar_documentacion_moto'),  
    path('moto/<str:pk>/mantenimiento/crear/', views.MantenimientoCreateView.as_view(), name='crear_mantenimiento'),

    # --- CRUD MOVIMIENTOS ---
    path('movimientos/', views.MovimientoListView.as_view(), name='movimiento_lista'),
    path('movimientos/crear/', views.MovimientoCreateView.as_view(), name='movimiento_crear'),
    path('movimientos/detalle/<int:pk>/', views.MovimientoDetailView.as_view(), name='movimiento_detalle'),
    path('movimientos/editar/<int:pk>/', views.MovimientoUpdateView.as_view(), name='movimiento_editar'),
    path('movimientos/eliminar/<int:pk>/', views.MovimientoDeleteView.as_view(), name='movimiento_eliminar'),
    
    # --- CRUD TRAMOS ---
    path('movimientos/detalle/<int:padre_pk>/crear-tramo/', views.TramoCreateView.as_view(), name='crear_tramo'),
    path('tramos/editar/<int:pk>/', views.TramoUpdateView.as_view(), name='tramo_editar'),
    path('tramos/eliminar/<int:pk>/', views.TramoDeleteView.as_view(), name='tramo_eliminar'),
    
    # --- VISTAS DE ASIGNACIÓN ---
    path('motorista/<int:motorista_pk>/asignar-farmacia/', views.AsignacionFarmaciaCreateView.as_view(), name='asignar_farmacia'),
    path('moto/<str:moto_pk>/asignar-motorista/', views.AsignacionMotoCreateView.as_view(), name='asignar_moto_motorista'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)