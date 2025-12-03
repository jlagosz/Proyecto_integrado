from django import forms
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q, Subquery, OuterRef
from django.http import HttpRequest
from django.utils import timezone
from collections import defaultdict
from datetime import timedelta
from django.http import JsonResponse

# --- AUTENTICACIÓN NATIVA DE DJANGO ---
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# --- MENSAJES ---
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from discopro.utils import render_to_pdf 


from .forms import (
    CustomLoginForm, UsuarioForm,
    FarmaciaForm, MotoristaForm, MotoForm, 
    AsignacionFarmaciaForm, AsignacionMotoForm, DocumentacionMotoForm, MantenimientoForm,
    ContactoEmergenciaForm, TipoMovimientoForm, MovimientoForm
)

# Importamos Modelos
from .models import (
    Farmacia, Motorista, Moto, AsignacionFarmacia, AsignacionMoto, DocumentacionMoto, Mantenimiento,
    ContactoEmergencia, TipoMovimiento, Movimiento, Usuario, Rol, Provincia, Comuna
)

# --- VISTAS DE LOGIN/LOGOUT (NATIVAS) ---

def login_view(request):
    """Maneja el inicio de sesión usando Django Auth."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) 
            messages.success(request, f"¡Bienvenido, {user.first_name}!")
            return redirect('index')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = CustomLoginForm()

    return render(request, 'discopro/login.html', {'form': form})

def logout_view(request):
    """Cierra la sesión nativa."""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

# --- VISTA PRINCIPAL (DASHBOARD) ---

@login_required
def index(request: HttpRequest):
    """Dashboard principal protegido por @login_required."""
    
    total_farmacias = Farmacia.objects.count()
    total_motoristas = Motorista.objects.count()
    total_motos = Moto.objects.count()
    total_usuarios = Usuario.objects.count()
    total_movimientos = Movimiento.objects.filter(movimiento_padre__isnull=True).count()

    context = {
        'total_farmacias': total_farmacias,
        'total_motoristas': total_motoristas,
        'total_motos': total_motos,
        'total_usuarios': total_usuarios,       
        'total_movimientos': total_movimientos,
        'usuario_logueado': request.user 
    }
    return render(request, "discopro/Main/dashboard.html", context)

# --- REPORTES ---

class ReporteMovimientosView(LoginRequiredMixin, TemplateView):
    template_name = 'discopro/Movimiento/reporte_general.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        ahora = timezone.now()
        hoy_local = timezone.localtime(ahora)
        
        inicio_dia = hoy_local.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        inicio_mes = hoy_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        inicio_anio = hoy_local.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        # 1. Diario
        qs_hoy = Movimiento.objects.filter(fecha_movimiento__gte=inicio_dia, fecha_movimiento__lt=fin_dia)
        context['total_hoy'] = qs_hoy.count()
        context['estados_hoy'] = qs_hoy.values('estado').annotate(total=Count('estado'))

        # 2. Mensual
        qs_mes = Movimiento.objects.filter(fecha_movimiento__gte=inicio_mes)
        context['total_mes'] = qs_mes.count()
        context['tipos_mes'] = qs_mes.values('tipo_movimiento__nombre').annotate(total=Count('tipo_movimiento'))

        # 3. Anual
        qs_anio = Movimiento.objects.filter(fecha_movimiento__gte=inicio_anio).order_by('fecha_movimiento')
        context['total_anio'] = qs_anio.count()
        
        datos_agrupados = defaultdict(int)
        for mov in qs_anio:
            fecha_local = timezone.localtime(mov.fecha_movimiento)
            mes_key = fecha_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            datos_agrupados[mes_key] += 1
            
        evolucion_anual_lista = []
        for fecha, cantidad in datos_agrupados.items():
            evolucion_anual_lista.append({'mes': fecha, 'total': cantidad})
        
        evolucion_anual_lista.sort(key=lambda x: x['mes'])
        context['evolucion_anual'] = evolucion_anual_lista

        return context

class ExportarReportePDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tipo = request.GET.get('tipo', 'diario')
        
        ahora = timezone.now()
        hoy_local = timezone.localtime(ahora)
        
        inicio_dia = hoy_local.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        inicio_mes = hoy_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        inicio_anio = hoy_local.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        data = {}
        titulo = ""
        movimientos = []

        if tipo == 'diario':
            titulo = f"Reporte Diario ({hoy_local.strftime('%d-%m-%Y')})"
            movimientos = Movimiento.objects.filter(fecha_movimiento__gte=inicio_dia, fecha_movimiento__lt=fin_dia)
            data['detalles'] = movimientos.values('estado').annotate(total=Count('estado'))
            data['columnas'] = ['Estado', 'Cantidad']

        elif tipo == 'mensual':
            titulo = f"Reporte Mensual ({hoy_local.strftime('%B %Y')})"
            movimientos = Movimiento.objects.filter(fecha_movimiento__gte=inicio_mes)
            data['detalles'] = movimientos.values('tipo_movimiento__nombre').annotate(total=Count('tipo_movimiento'))
            data['columnas'] = ['Tipo de Movimiento', 'Cantidad']

        elif tipo == 'anual':
            titulo = f"Reporte Anual ({hoy_local.year})"
            movimientos = Movimiento.objects.filter(fecha_movimiento__gte=inicio_anio).order_by('fecha_movimiento')
            
            datos_agrupados = defaultdict(int)
            for mov in movimientos:
                fecha_local = timezone.localtime(mov.fecha_movimiento)
                mes_key = fecha_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                datos_agrupados[mes_key] += 1
            
            lista_anual = []
            for fecha, cantidad in datos_agrupados.items():
                nombre_mes = fecha.strftime('%B')
                lista_anual.append({'nombre': nombre_mes, 'total': cantidad})
            
            lista_anual.sort(key=lambda x: x['nombre'])
            data['detalles'] = lista_anual
            data['columnas'] = ['Mes', 'Cantidad']
            data['es_anual'] = True

        context = {
            'titulo': titulo,
            'fecha_impresion': hoy_local,
            'usuario': request.user,
            'data': data,
            'total_general': movimientos.count() if hasattr(movimientos, 'count') else len(movimientos)
        }
        return render_to_pdf('discopro/Movimiento/reporte_pdf.html', context)

# --- CRUD USUARIOS  ---

class UsuarioListView(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'discopro/Usuario/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('rol')
        query = self.request.GET.get('q')
        if query:
            # Adaptamos filtros a los campos de AbstractUser (username, first_name, last_name)
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(rut__icontains=query) |
                Q(username__icontains=query)
            ).distinct()
        return queryset.order_by('first_name')

class UsuarioCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'discopro/Usuario/usuario_form.html'
    success_url = reverse_lazy('usuario_lista')
    success_message = "Usuario creado exitosamente."

class UsuarioUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'discopro/Usuario/usuario_form.html'
    success_url = reverse_lazy('usuario_lista')
    success_message = "Usuario actualizado exitosamente."

class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('usuario_lista')
    
    def form_valid(self, form):
        messages.success(self.request, "Usuario eliminado exitosamente.")
        return super().form_valid(form)

# --- CRUD FARMACIAS ---

class FarmaciaListView(LoginRequiredMixin, ListView):
    model = Farmacia
    template_name = 'discopro/Farmacia/farmacia_list.html'
    context_object_name = 'farmacias'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('comuna__provincia__region')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) | 
                Q(direccion__icontains=query) |
                Q(comuna__nombreComuna__icontains=query)
            ).distinct()
        return queryset

class FarmaciaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'discopro/Farmacia/farmacia_form.html'
    success_url = reverse_lazy('farmacia_lista')
    success_message = "Farmacia creada exitosamente."

class FarmaciaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'discopro/Farmacia/farmacia_form.html'
    success_url = reverse_lazy('farmacia_lista')
    success_message = "Farmacia actualizada exitosamente."

class FarmaciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Farmacia
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('farmacia_lista')
    
    def form_valid(self, form):
        messages.success(self.request, "Farmacia eliminada exitosamente.")
        return super().form_valid(form)
    
class FarmaciaDetailView(LoginRequiredMixin, DetailView):
    model = Farmacia
    template_name = 'discopro/Farmacia/farmacia_detail.html'
    context_object_name = 'farmacia'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['farmacia'] = Farmacia.objects.select_related('comuna__provincia__region').get(pk=self.object.pk)
        return context

# --- CRUD MOTORISTAS ---

class MotoristaListView(LoginRequiredMixin, ListView):
    model = Motorista
    template_name = 'discopro/Motorista/motorista_list.html'
    context_object_name = 'motoristas'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('comuna')
        query = self.request.GET.get('q')

        latest_farmacia = AsignacionFarmacia.objects.filter(
            motorista=OuterRef('pk')
        ).order_by('-fechaAsignacion', '-idAsignacionFarmacia').values('farmacia__nombre')[:1]
        
        queryset = queryset.annotate(farmacia_actual=Subquery(latest_farmacia))

        if query:
            queryset = queryset.filter(
                Q(nombres__icontains=query) | 
                Q(rut__icontains=query) |
                Q(comuna__nombreComuna__icontains=query)
            ).distinct()
        return queryset

class MotoristaDetailView(LoginRequiredMixin, DetailView):
    model = Motorista
    template_name = 'discopro/Motorista/motorista_detail.html'
    context_object_name = 'motorista'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motorista = self.get_object()
        context['asignaciones_farmacia'] = AsignacionFarmacia.objects.filter(motorista=motorista).select_related('farmacia').order_by('-fechaAsignacion')
        context['asignaciones_moto'] = AsignacionMoto.objects.filter(motorista=motorista).select_related('moto').order_by('-fechaAsignacion')
        context['contactos'] = motorista.contactos_emergencia.all()
        return context

class MotoristaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'discopro/Motorista/motorista_form.html'
    success_url = reverse_lazy('motorista_lista')
    success_message = "Motorista registrado exitosamente."

class MotoristaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'discopro/Motorista/motorista_form.html'
    success_url = reverse_lazy('motorista_lista')
    success_message = "Datos del motorista actualizados correctamente."

class MotoristaDeleteView(LoginRequiredMixin, DeleteView):
    model = Motorista
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('motorista_lista')
    
    def form_valid(self, form):
        messages.success(self.request, "Motorista eliminado exitosamente.")
        return super().form_valid(form)

# --- CRUD MOTOS ---

class MotoListView(LoginRequiredMixin, ListView):
    model = Moto
    template_name = 'discopro/Moto/moto_list.html'
    context_object_name = 'motos'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        latest_motorista = AsignacionMoto.objects.filter(
            moto=OuterRef('pk')
        ).order_by('-fechaAsignacion', '-idAsignacionMoto').values('motorista__nombres')[:1]
        
        queryset = queryset.annotate(motorista_actual=Subquery(latest_motorista))
        if query:
            queryset = queryset.filter(Q(patente__icontains=query) | Q(marca__icontains=query)).distinct()
        return queryset

class MotoDetailView(LoginRequiredMixin, DetailView):
    model = Moto
    template_name = 'discopro/Moto/moto_detail.html'
    context_object_name = 'moto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        moto = self.get_object()
        context['asignaciones_moto'] = AsignacionMoto.objects.filter(moto=moto).select_related('motorista').order_by('-fechaAsignacion')
        return context

class MotoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Moto
    form_class = MotoForm
    template_name = 'discopro/Moto/moto_form.html'
    success_url = reverse_lazy('moto_lista')
    success_message = "Moto registrada exitosamente."

class MotoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Moto
    form_class = MotoForm
    template_name = 'discopro/Moto/moto_form.html'
    success_url = reverse_lazy('moto_lista')
    success_message = "Datos de la moto actualizados."

class MotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Moto
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('moto_lista')
    
    def form_valid(self, form):
        messages.success(self.request, "Moto eliminada exitosamente.")
        return super().form_valid(form)

# --- ASIGNACIONES Y DOCUMENTOS ---

class AsignacionFarmaciaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AsignacionFarmacia
    form_class = AsignacionFarmaciaForm
    template_name = 'discopro/Asignaciones/asignacion_farmacia_form.html'
    success_message = "Farmacia asignada correctamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motorista'] = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        return context
        
    def form_valid(self, form):
        form.instance.motorista = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('motorista_detalle', kwargs={'pk': self.kwargs['motorista_pk']})

class AsignacionMotoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AsignacionMoto
    form_class = AsignacionMotoForm
    template_name = 'discopro/Asignaciones/asignacion_moto_form.html'
    success_message = "Moto asignada correctamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moto'] = get_object_or_404(Moto, pk=self.kwargs['moto_pk'])
        return context

    def form_valid(self, form):
        form.instance.moto = get_object_or_404(Moto, pk=self.kwargs['moto_pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('moto_detalle', kwargs={'pk': self.kwargs['moto_pk']})
    
class DocumentacionMotoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = DocumentacionMoto
    form_class = DocumentacionMotoForm
    template_name = 'discopro/Moto/documentacion_moto_form.html'
    success_message = "Documentación actualizada correctamente."

    def get_object(self, queryset=None):
        moto_patente = self.kwargs.get('pk') 
        doc, created = DocumentacionMoto.objects.get_or_create(
            moto_id=moto_patente, defaults={'anio': timezone.now().year}
        )
        return doc

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moto'] = self.get_object().moto
        return context

    def get_success_url(self):
        return reverse_lazy('moto_detalle', kwargs={'pk': self.object.moto_id})

class MantenimientoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'discopro/Moto/mantenimiento_form.html'
    success_message = "Mantenimiento registrado exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moto'] = get_object_or_404(Moto, pk=self.kwargs.get('pk'))
        return context

    def form_valid(self, form):
        form.instance.moto = get_object_or_404(Moto, pk=self.kwargs.get('pk'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('moto_detalle', kwargs={'pk': self.object.moto.pk})

class ContactoEmergenciaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ContactoEmergencia
    form_class = ContactoEmergenciaForm
    template_name = 'discopro/Motorista/contacto_emergencia_form.html'
    success_message = "Contacto añadido."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motorista'] = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        return context

    def form_valid(self, form):
        form.instance.motorista = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('motorista_detalle', kwargs={'pk': self.kwargs['motorista_pk']})

class ContactoEmergenciaDeleteView(LoginRequiredMixin, DeleteView):
    model = ContactoEmergencia
    template_name = 'discopro/confirmar_eliminar.html'
    
    def get_success_url(self):
        return reverse_lazy('motorista_detalle', kwargs={'pk': self.object.motorista.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Contacto eliminado exitosamente.")
        return super().form_valid(form)

# --- CRUD MOVIMIENTOS ---

class MovimientoListView(LoginRequiredMixin, ListView):
    model = Movimiento
    template_name = 'discopro/Movimiento/movimiento_list.html'
    context_object_name = 'movimientos'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(movimiento_padre__isnull=True).order_by('-fecha_movimiento')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(numero_despacho__icontains=query) |
                Q(id_movimiento__icontains=query) |
                Q(origen__icontains=query) |
                Q(destino__icontains=query) |
                Q(usuario_responsable__first_name__icontains=query) # Filtro por first_name del User
            ).distinct()
        return queryset

class MovimientoDetailView(LoginRequiredMixin, DetailView):
    model = Movimiento
    template_name = 'discopro/Movimiento/movimiento_detail.html'
    context_object_name = 'movimiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tramos_hijos'] = Movimiento.objects.filter(movimiento_padre=self.object).order_by('fecha_movimiento')
        return context

class MovimientoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/movimiento_padre_form.html'
    success_message = "Movimiento (Despacho) creado exitosamente."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['movimiento_padre'].widget = forms.HiddenInput()
        return form

    def get_initial(self):
        initial = super().get_initial()
        initial['movimiento_padre'] = None
        return initial

    def get_success_url(self):
        return self.object.get_absolute_url()

class MovimientoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/movimiento_padre_form.html'
    success_message = "Movimiento actualizado correctamente."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['movimiento_padre'].widget = forms.HiddenInput()
        return form

    def get_success_url(self):
        return self.object.get_absolute_url()

class MovimientoDeleteView(LoginRequiredMixin, DeleteView):
    model = Movimiento
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('movimiento_lista')
    
    def form_valid(self, form):
        messages.success(self.request, "Movimiento eliminado exitosamente.")
        return super().form_valid(form)

class TramoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/tramo_form.html'
    success_message = "Tramo añadido exitosamente."

    def get_movimiento_padre(self):
        return get_object_or_404(Movimiento, pk=self.kwargs['padre_pk'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['movimiento_padre'].widget = forms.HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimiento_padre'] = self.get_movimiento_padre()
        return context

    def get_initial(self):
        initial = super().get_initial()
        padre = self.get_movimiento_padre()
        tramos_previos = Movimiento.objects.filter(movimiento_padre=padre).order_by('fecha_movimiento')
        ultimo_tramo = tramos_previos.last()

        initial['movimiento_padre'] = padre
        initial['usuario_responsable'] = padre.usuario_responsable
        initial['motorista_asignado'] = padre.motorista_asignado
        initial['estado'] = 'pendiente'

        if ultimo_tramo:
            initial['origen'] = ultimo_tramo.destino 
        else:
            initial['origen'] = padre.origen
        
        initial['destino'] = padre.destino 
        return initial

    def get_success_url(self):
        return reverse_lazy('movimiento_detalle', kwargs={'pk': self.kwargs['padre_pk']})
    
    def dispatch(self, request, *args, **kwargs):
        padre = self.get_movimiento_padre()
        
        if padre.estado != 'pendiente':
            messages.error(request, "No se pueden agregar tramos a un despacho completado o anulado.")
            return redirect('movimiento_detalle', pk=padre.pk)
            
        return super().dispatch(request, *args, **kwargs)

class TramoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/tramo_form.html'
    success_message = "Tramo actualizado correctamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimiento_padre'] = self.object.movimiento_padre
        return context

    def get_success_url(self):
        return reverse_lazy('movimiento_detalle', kwargs={'pk': self.object.movimiento_padre.pk})

class TramoDeleteView(LoginRequiredMixin, DeleteView):
    model = Movimiento
    template_name = 'discopro/confirmar_eliminar.html'
    
    def form_valid(self, form):
        messages.success(self.request, "Tramo eliminado exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('movimiento_detalle', kwargs={'pk': self.object.movimiento_padre.pk})


# --- VISTAS AJAX  ---
def load_provincias(request):
    region_id = request.GET.get('region')
    provincias = Provincia.objects.filter(region_id=region_id).order_by('nombreProvincia')
    return JsonResponse(list(provincias.values('idProvincia', 'nombreProvincia')), safe=False)

def load_comunas(request):
    provincia_id = request.GET.get('provincia')
    comunas = Comuna.objects.filter(provincia_id=provincia_id).order_by('nombreComuna')
    return JsonResponse(list(comunas.values('idComuna', 'nombreComuna')), safe=False)