from django.utils import timezone
from django.db.models import Q, Subquery, OuterRef
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.http import HttpRequest
from django.contrib import messages
from .forms import LoginForm

# Importamos los modelos
from .models import (
    Farmacia, Motorista, Moto, AsignacionFarmacia, AsignacionMoto, DocumentacionMoto, Mantenimiento,
    ContactoEmergencia, TipoMovimiento, Movimiento, Usuario, Rol
)

# Importamos los formularios
from .forms import (
    FarmaciaForm, MotoristaForm, MotoForm, 
    AsignacionFarmaciaForm, AsignacionMotoForm, DocumentacionMotoForm, MantenimientoForm,
    ContactoEmergenciaForm, TipoMovimientoForm, MovimientoForm, UsuarioForm
)

# --- SEGURIDAD ---
class LoginRequiredMixin:
    """
    Este Mixin protege las Vistas Basadas en Clases (CBV).
    Verifica si 'usuario_id' está en la sesión antes de mostrar la página.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        try:
            request.usuario = Usuario.objects.get(pk=request.session.get('usuario_id'))
        except Usuario.DoesNotExist:
            del request.session['usuario_id']
            messages.error(request, "Tu sesión ha expirado. Por favor, inicia sesión de nuevo.")
            return redirect('login')
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_logueado'] = self.request.usuario
        return context


# --- VISTA PRINCIPAL ---
def index(request: HttpRequest):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        del request.session['usuario_id']
        messages.error(request, "Tu sesión ha expirado.")
        return redirect('login')

    total_farmacias = Farmacia.objects.count()
    total_motoristas = Motorista.objects.count()
    total_motos = Moto.objects.count()
    
    context = {
        'total_farmacias': total_farmacias,
        'total_motoristas': total_motoristas,
        'total_motos': total_motos,
        'usuario_logueado': usuario
    }
    return render(request, "discopro/Main/Index.html", context)

# --- CRUD USUARIOS ---
class UsuarioListView(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'discopro/Usuario/usuario_list.html'
    context_object_name = 'usuarios'
    def get_queryset(self):
        queryset = super().get_queryset().select_related('rol')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(rut__icontains=query) |
                Q(nombreUsuario__icontains=query)
            ).distinct()
        return queryset.order_by('nombres')

class UsuarioCreateView(LoginRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'discopro/Usuario/usuario_form.html'
    success_url = reverse_lazy('usuario_lista')

class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'discopro/Usuario/usuario_form.html'
    success_url = reverse_lazy('usuario_lista')

class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('usuario_lista')

# --- CRUD FARMACIAS ---
class FarmaciaListView(LoginRequiredMixin, ListView):
    model = Farmacia
    template_name = 'discopro/Farmacia/Lista.html'
    context_object_name = 'farmacias'
    def get_queryset(self):
        queryset = super().get_queryset().select_related('comuna__provincia__region')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) | 
                Q(direccion__icontains=query) |
                Q(comuna__nombreComuna__icontains=query) |
                Q(comuna__provincia__nombreProvincia__icontains=query)
            ).distinct()
        return queryset

class FarmaciaCreateView(LoginRequiredMixin, CreateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'discopro/Farmacia/agregar_editar.html'
    success_url = reverse_lazy('farmacia_lista')

class FarmaciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'discopro/Farmacia/agregar_editar.html'
    success_url = reverse_lazy('farmacia_lista')

class FarmaciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Farmacia
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('farmacia_lista')
    
class FarmaciaDetailView(LoginRequiredMixin, DetailView):
    model = Farmacia
    template_name = 'discopro/Farmacia/detalle.html'
    context_object_name = 'farmacia'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['farmacia'] = Farmacia.objects.select_related(
            'comuna__provincia__region'
        ).get(pk=self.object.pk)
        return context

# --- CRUD MOTORISTAS ---
class MotoristaListView(LoginRequiredMixin, ListView):
    model = Motorista
    template_name = 'discopro/Motorista/ListarMotorista.html'
    context_object_name = 'motoristas'
    def get_queryset(self):
        queryset = super().get_queryset().select_related('comuna')
        query = self.request.GET.get('q')
        latest_farmacia = AsignacionFarmacia.objects.filter(
            motorista=OuterRef('pk')
        ).order_by('-fechaAsignacion').values('farmacia__nombre')[:1]
        queryset = queryset.annotate(
            farmacia_actual=Subquery(latest_farmacia)
        )
        if query:
            queryset = queryset.filter(
                Q(nombres__icontains=query) | 
                Q(rut__icontains=query) |
                Q(comuna__nombreComuna__icontains=query)
            ).distinct()
        return queryset

class MotoristaDetailView(LoginRequiredMixin, DetailView):
    model = Motorista
    template_name = 'discopro/Motorista/detalleMotorista.html'
    context_object_name = 'motorista'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motorista = self.get_object()
        context['asignaciones_farmacia'] = AsignacionFarmacia.objects.filter(
            motorista=motorista
        ).select_related('farmacia').order_by('-fechaAsignacion')
        context['asignaciones_moto'] = AsignacionMoto.objects.filter(
            motorista=motorista
        ).select_related('moto').order_by('-fechaAsignacion')
        context['contactos'] = motorista.contactos_emergencia.all()
        return context

class MotoristaCreateView(LoginRequiredMixin, CreateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'discopro/Motorista/agregar_editar.html'
    success_url = reverse_lazy('motorista_lista')

class MotoristaUpdateView(LoginRequiredMixin, UpdateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'discopro/Motorista/agregar_editar.html'
    success_url = reverse_lazy('motorista_lista')

class MotoristaDeleteView(LoginRequiredMixin, DeleteView):
    model = Motorista
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('motorista_lista')

# --- CRUD MOTOS ---
class MotoListView(LoginRequiredMixin, ListView):
    model = Moto
    template_name = 'discopro/Moto/ListarMoto.html'
    context_object_name = 'motos'
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        latest_motorista = AsignacionMoto.objects.filter(
            moto=OuterRef('pk')
        ).order_by('-fechaAsignacion').values('motorista__nombres')[:1]
        queryset = queryset.annotate(
            motorista_actual=Subquery(latest_motorista)
        )
        if query:
            queryset = queryset.filter(
                Q(patente__icontains=query) | 
                Q(marca__icontains=query)
            ).distinct()
        return queryset

class MotoDetailView(LoginRequiredMixin, DetailView):
    model = Moto
    template_name = 'discopro/Moto/detalleMoto.html'
    context_object_name = 'moto'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        moto = self.get_object()
        context['asignaciones_moto'] = AsignacionMoto.objects.filter(
            moto=moto
        ).select_related('motorista').order_by('-fechaAsignacion')
        return context

class MotoCreateView(LoginRequiredMixin, CreateView):
    model = Moto
    form_class = MotoForm
    template_name = 'discopro/Moto/agregar_editar.html'
    success_url = reverse_lazy('moto_lista')

class MotoUpdateView(LoginRequiredMixin, UpdateView):
    model = Moto
    form_class = MotoForm
    template_name = 'discopro/Moto/agregar_editar.html'
    success_url = reverse_lazy('moto_lista')

class MotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Moto
    template_name = 'discopro/confirmar_eliminar.html'
    success_url = reverse_lazy('moto_lista')

# --- VISTAS PARA ASIGNACIONES ---
class AsignacionFarmaciaCreateView(LoginRequiredMixin, CreateView):
    model = AsignacionFarmacia
    form_class = AsignacionFarmaciaForm
    template_name = 'discopro/Asignaciones/asignar_farmacia.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motorista'] = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        return context
    def form_valid(self, form):
        motorista = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        form.instance.motorista = motorista
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('detalle_motorista', kwargs={'pk': self.kwargs['motorista_pk']})

class AsignacionMotoCreateView(LoginRequiredMixin, CreateView):
    model = AsignacionMoto
    form_class = AsignacionMotoForm
    template_name = 'discopro/Asignaciones/asignar_moto.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moto'] = get_object_or_404(Moto, pk=self.kwargs['moto_pk'])
        return context
    def form_valid(self, form):
        moto = get_object_or_404(Moto, pk=self.kwargs['moto_pk'])
        form.instance.moto = moto
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('detalle_moto', kwargs={'pk': self.kwargs['moto_pk']})
    
class DocumentacionMotoUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentacionMoto
    form_class = DocumentacionMotoForm
    template_name = 'discopro/Moto/gestionar_documentacion.html'
    def get_object(self, queryset=None):
        moto_patente = self.kwargs.get('pk') 
        documentacion, created = DocumentacionMoto.objects.get_or_create(
            moto_id=moto_patente, 
            defaults={'anio': timezone.now().year}
        )
        return documentacion
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moto'] = self.get_object().moto
        return context
    def get_success_url(self):
        return reverse_lazy('detalle_moto', kwargs={'pk': self.object.moto_id})

class MantenimientoCreateView(LoginRequiredMixin, CreateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'discopro/Moto/crear_mantenimiento.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moto'] = get_object_or_404(Moto, pk=self.kwargs.get('pk'))
        return context
    def form_valid(self, form):
        moto = get_object_or_404(Moto, pk=self.kwargs.get('pk'))
        form.instance.moto = moto
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('detalle_moto', kwargs={'pk': self.object.moto.pk})

class ContactoEmergenciaCreateView(LoginRequiredMixin, CreateView):
    model = ContactoEmergencia
    form_class = ContactoEmergenciaForm
    template_name = 'discopro/Motorista/crear_contacto.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motorista'] = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        return context
    def form_valid(self, form):
        motorista = get_object_or_404(Motorista, pk=self.kwargs['motorista_pk'])
        form.instance.motorista = motorista
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('detalle_motorista', kwargs={'pk': self.kwargs['motorista_pk']})
    
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
                Q(id_movimiento__icontains=query) |
                Q(origen__icontains=query) |
                Q(destino__icontains=query) |
                Q(usuario_responsable__nombres__icontains=query) |
                Q(motorista_asignado__nombres__icontains=query)
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

class MovimientoCreateView(LoginRequiredMixin, CreateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/movimiento_padre_form.html'
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

class MovimientoUpdateView(LoginRequiredMixin, UpdateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/movimiento_padre_form.html'
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

class TramoCreateView(LoginRequiredMixin, CreateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/tramo_form.html'
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

class TramoUpdateView(LoginRequiredMixin, UpdateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'discopro/Movimiento/tramo_form.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimiento_padre'] = self.object.movimiento_padre
        return context
    def get_success_url(self):
        return reverse_lazy('movimiento_detalle', kwargs={'pk': self.object.movimiento_padre.pk})

class TramoDeleteView(LoginRequiredMixin, DeleteView):
    model = Movimiento
    template_name = 'discopro/confirmar_eliminar.html'
    def get_success_url(self):
        return reverse_lazy('movimiento_detalle', kwargs={'pk': self.object.movimiento_padre.pk})


# --- VISTAS DE LOGIN/LOGOUT ---

def login_view(request: HttpRequest):
    """
    Maneja el inicio de sesión del usuario.
    """
    if request.session.get('usuario_id'):
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            nombreUsuario = form.cleaned_data['nombreUsuario']
            contrasena = form.cleaned_data['contrasena']
            
            try:
                usuario = Usuario.objects.get(nombreUsuario=nombreUsuario)
            except Usuario.DoesNotExist:
                usuario = None

            if usuario is not None and usuario.check_password(contrasena):
                request.session['usuario_id'] = usuario.idUsuario
                request.session['usuario_nombre'] = f"{usuario.nombres} {usuario.apellidos}" # Guardamos el nombre para mostrarlo
                return redirect('index')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'discopro/login.html', {'form': form})


def logout_view(request: HttpRequest):
    """
    Limpia la sesión y cierra la sesión del usuario.
    """
    try:
        del request.session['usuario_id']
        del request.session['usuario_nombre']
    except KeyError:
        pass
    
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')