from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Perfil 
from recetas.forms import FormularioReceta 
from .forms import (
    FormularioRegistro,
    FormularioLogin,
    FormularioEditarPerfil,
    FormularioCambiarContrasena
)
from .models import Perfil 

from recetas.models import Receta, RecetaIngrediente, Ingrediente

def perfil_publico(request, username):
    user_obj = get_object_or_404(User, username=username, is_active=True)
    perfil = user_obj.perfil
    recetas_del_usuario = Receta.objects.filter(creado_por=user_obj).order_by('-fecha_creacion').prefetch_related(
        'recetaingrediente_set__ingrediente'
    )
    context = {
        'perfil': perfil,
        'es_perfil_propio': request.user.is_authenticated and perfil.usuario == request.user,
        'recetas_usuario': recetas_del_usuario,
    }
    return render(request, 'usuario/perfil_publico.html', context)

def registro_usuario(request):
    if request.user.is_authenticated:
        return redirect('usuario:perfil')
    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
                    return redirect('usuario:perfil_usuario')
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormularioRegistro()
    return render(request, 'usuario/registro.html', {'form': form})

def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('usuario:perfil')
    if request.method == 'POST':
        form = FormularioLogin(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de vuelta, {user.username}!')
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('inicio')
            else: 
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else: 
            messages.error(request, 'Usuario o contraseña incorrectos.') 
    else:
        form = FormularioLogin()
    return render(request, 'usuario/login.html', {'form': form})
@login_required
def logout_usuario(request):
    nombre_usuario = request.user.username
    logout(request)
    messages.success(request, f'¡Hasta luego, {nombre_usuario}!')
    return redirect('usuario:login')

@login_required
def perfil_usuario(request):
    usuario_actual = request.user
    perfil, created = Perfil.objects.get_or_create(usuario=usuario_actual)
    recetas_del_usuario = Receta.objects.filter(creado_por=usuario_actual)\
        .order_by('-fecha_creacion')\
        .prefetch_related('recetaingrediente_set__ingrediente')
    print(f"Usuario actual: {usuario_actual.username} (ID: {usuario_actual.id})")
    print(f"Recetas encontradas: {recetas_del_usuario.count()}")
    for receta in recetas_del_usuario:
        print(f" - {receta.nombre} (creado por {receta.creado_por.username})")
    if request.method == 'POST' and 'eliminar_receta' in request.POST:
        receta_id = request.POST.get('receta_id')
        if receta_id:
            try:
                receta = get_object_or_404(Receta, id=receta_id, creado_por=usuario_actual)
                with transaction.atomic():
                    receta.delete()
                messages.success(request, 'Receta eliminada exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la receta: {e}')
        return redirect('usuario:perfil_usuario')  
    context = {
        'perfil': perfil,
        'usuario': usuario_actual,
        'recetas_del_usuario': recetas_del_usuario,
        'es_perfil_propio': True,  
    }
    return render(request, 'usuario/perfil.html', context)

@login_required
def mi_perfil_con_gestion_recetas(request):
    usuario_actual = request.user
    perfil, created = Perfil.objects.get_or_create(usuario=usuario_actual)
    recetas_del_usuario = Receta.objects.filter(creado_por=usuario_actual).order_by('-fecha_creacion').prefetch_related(
        'recetaingrediente_set__ingrediente'
    )
    print(f"Usuario actual: {usuario_actual.username} (ID: {usuario_actual.id})")
    print(f"Recetas encontradas para {usuario_actual.username}: {recetas_del_usuario.count()}")
    for receta in recetas_del_usuario:
        print(f" - Receta: {receta.nombre}, Creado por: {receta.creado_por.username}")
    if request.method == 'POST' and 'eliminar_receta' in request.POST:
        receta_id_a_eliminar = request.POST.get('receta_id')
        if receta_id_a_eliminar:
            try:
                receta = get_object_or_404(Receta, id=receta_id_a_eliminar, creado_por=usuario_actual)
                with transaction.atomic():
                    receta.delete()
                messages.success(request, 'Receta eliminada exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la receta: {e}')
        return redirect('usuarios:mi_perfil_con_gestion_recetas')

    context = {
        'perfil': perfil,
        'recetas_del_usuario': recetas_del_usuario,
        'es_perfil_propio': True,
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def editar_perfil(request):
    """Vista para editar el perfil del usuario"""
    perfil = request.user.perfil
    if request.method == 'POST':
        form = FormularioEditarPerfil(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
                    return redirect('usuario:perfil_usuario')
            except Exception as e:
                messages.error(request, f'Error al actualizar el perfil: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormularioEditarPerfil(instance=perfil)
    return render(request, 'usuario/editar_perfil.html', {
        'form': form,
        'perfil': perfil
    })

    
@login_required
def cambiar_contrasena(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        form = FormularioCambiarContrasena(request.user, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
                return redirect('usuario:perfil_usuario')
            except Exception as e:
                messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormularioCambiarContrasena(request.user)
    return render(request, 'usuario/cambiar_contrasena.html', {'form': form})

@login_required
def configuracion_cuenta(request):
    perfil = request.user.perfil 
    context = {
        'perfil': perfil,
        'usuario': request.user,
    }
    return render(request, 'usuario/configuracion.html', context)

@login_required
@require_http_methods(["POST"])
def desactivar_cuenta(request):
    if request.method == 'POST':
        confirmacion = request.POST.get('confirmacion')
        if confirmacion == 'DESACTIVAR':
            try:
                with transaction.atomic():
                    perfil = request.user.perfil
                    request.user.is_active = False
                    request.user.save()
                    logout(request)
                    messages.success(request, 'Tu cuenta ha sido desactivada exitosamente.')
                    return redirect('usuario:login')
            except Exception as e:
                messages.error(request, f'Error al desactivar la cuenta: {str(e)}')
        else:
            messages.error(request, 'Confirmación incorrecta.')
    return redirect('usuario:configuracion')



@login_required
def lista_usuarios(request):
    usuario_actual = request.user
    usuarios_a_mostrar = User.objects.filter(
        is_active=True,
        perfil__isnull=False 
    ).exclude(
        id=usuario_actual.id 
    ).order_by('username')
    paginator = Paginator(usuarios_a_mostrar, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'usuarios': page_obj, 
        'page_obj': page_obj,
    }
    return render(request, 'usuario/lista_usuarios.html', context)

@login_required
def ajax_verificar_usuario(request):
    if request.method == 'GET':
        nombre_usuario_a_verificar = request.GET.get('nombre_usuario')
        if nombre_usuario_a_verificar:
            existe = User.objects.filter(username=nombre_usuario_a_verificar).exclude(pk=request.user.pk).exists()
            return JsonResponse({
                'disponible': not existe,
                'mensaje': 'Nombre de usuario disponible' if not existe else 'Nombre de usuario ya en uso'
            })
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)
