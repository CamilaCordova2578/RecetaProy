from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.views import LoginView, LogoutView
from .forms import FormularioReceta, RecetaIngredienteFormSet, RecetaForm
from .models import Receta, Ingrediente, RecetaIngrediente, Favorito, Usuario
from .forms import FormularioRegistroUsuario, FormularioReceta, FormularioIngrediente, FormularioBusqueda
from django.db.models import Q
from .models import Receta, Ingrediente

def buscador_global(request):
    query = request.GET.get('q', '')
    resultados = []
    sugerencias = []

    if query:
        resultados = Receta.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__icontains=query) |
            Q(recetaingrediente__ingrediente__nombre__icontains=query)
        ).distinct()
        sugerencias = resultados[:10]
    context = {
        'query': query,
        'resultados': resultados,
        'sugerencias': sugerencias
    }
    return render(request, 'recetas/resultados_busqueda.html', context)


def sugerencias_ajax(request):
    query = request.GET.get('q', '')
    sugerencias = []
    if query:
        recetas = Receta.objects.filter(
        Q(nombre__istartswith=query) |
        Q(recetaingrediente__ingrediente__nombre__istartswith=query)
    ).distinct()[:10]
        
        for receta in recetas:
            sugerencias.append({
                'nombre': receta.nombre,
                'id': receta.id
            })
    return JsonResponse({'sugerencias': sugerencias})



def inicio(request):
    recetas = Receta.objects.all()[:6]
    return render(request, 'recetas/inicio.html', {'recetas': recetas})

def registro_usuario(request):
    if request.method == 'POST':
        form = FormularioRegistroUsuario(request.POST)
        if form.is_valid():
            user = form.save()
            Usuario.objects.create(
                user=user,
                nombre_usuario=form.cleaned_data['nombre_usuario'],
                email=form.cleaned_data['email'],
            )
            login(request, user)
            messages.success(request, 'Usuario registrado exitosamente.')
            return redirect('inicio')
    else:
        form = FormularioRegistroUsuario()
    return render(request, 'recetas/registro.html', {'form': form})

@login_required
def lista_recetas(request):
    form = FormularioBusqueda(request.GET)
    recetas = Receta.objects.all()

    if form.is_valid() and form.cleaned_data['ingrediente']:
        ingrediente_buscar = form.cleaned_data['ingrediente']
        recetas = recetas.filter(
            recetaingrediente__ingrediente__nombre__icontains=ingrediente_buscar
        ).distinct()


    recetas_favoritas_ids = set()
    if request.user.is_authenticated:
        recetas_favoritas_ids = set(
            Favorito.objects.filter(usuario=request.user).values_list('receta_id', flat=True)
        )

    return render(request, 'recetas/lista_recetas.html', {
        'recetas': recetas,
        'form': form,
        'recetas_favoritas_ids': recetas_favoritas_ids
    })

def detalle_receta(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)
    ingredientes = RecetaIngrediente.objects.filter(receta=receta)
    es_favorito = False

    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, receta=receta).exists()

    return render(request, 'recetas/detalle_receta.html', {
        'receta': receta,
        'ingredientes': ingredientes,
        'es_favorito': es_favorito
    })


@login_required
def perfil_usuario(request):
    recetas_del_usuario = Receta.objects.filter(creado_por=request.user).order_by('-fecha_creacion')


    if 'crear_receta' in request.POST:
        form_creacion = FormularioReceta(request.POST, request.FILES)
        if form_creacion.is_valid():
            with transaction.atomic():
                receta = form_creacion.save(commit=False)
                receta.creado_por = request.user
                receta.save()
            messages.success(request, 'Receta creada exitosamente.')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Error al crear la receta. Por favor, revisa los campos.')
    else:
        form_creacion = FormularioReceta()

    if 'eliminar_receta' in request.POST:
        receta_id_a_eliminar = request.POST.get('receta_id')
        if receta_id_a_eliminar:
            try:
                receta = get_object_or_404(Receta, id=receta_id_a_eliminar, creado_por=request.user)
                with transaction.atomic():
                    receta.delete()
                messages.success(request, 'Receta eliminada exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la receta: {e}')
        return redirect('perfil_usuario')

    favoritos_del_usuario = Favorito.objects.filter(usuario=request.user)
    recetas_favoritas = [fav.receta for fav in favoritos_del_usuario]

    context = {
        'recetas_del_usuario': recetas_del_usuario,
        'form_creacion': form_creacion,
        'recetas_favoritas': recetas_favoritas,
    }
    return render(request, 'recetas/perfil_usuario.html', context)


@login_required
def editar_receta(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id, creado_por=request.user)
    
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES, instance=receta)
        formset = RecetaIngredienteFormSet(request.POST, instance=receta)
        if form.is_valid() and formset.is_valid():
            receta_actualizada = form.save()
            formset.instance = receta_actualizada
            formset.save()
            
            messages.success(request, 'Receta actualizada exitosamente!')
            return redirect('detalle_receta', receta_id=receta_actualizada.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RecetaForm(instance=receta)
        formset = RecetaIngredienteFormSet(instance=receta)
    
    context = {
        'form': form,
        'formset': formset,
        'receta': receta,
        'ingredientes': Ingrediente.objects.all()
    }
    
    return render(request, 'recetas/editar_receta.html', context)

@login_required
def agregar_ingrediente_ajax(request):
    """Vista AJAX para agregar nuevos ingredientes dinámicamente"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        unidad_medida = request.POST.get('unidad_medida', 'unidad')
        
        if nombre:
            ingrediente, created = Ingrediente.objects.get_or_create(
                nombre=nombre,
                defaults={'unidad_medida': unidad_medida}
            )
            
            return JsonResponse({
                'success': True,
                'ingrediente_id': ingrediente.id,
                'ingrediente_nombre': ingrediente.nombre,
                'unidad_medida': ingrediente.unidad_medida,
                'created': created
            })
    
    return JsonResponse({'success': False})

@login_required
def eliminar_ingrediente_receta(request, receta_id, ingrediente_id):
    """Vista para eliminar un ingrediente de una receta"""
    if request.method == 'POST':
        receta = get_object_or_404(Receta, id=receta_id, creado_por=request.user)
        try:
            receta_ingrediente = RecetaIngrediente.objects.get(
                receta=receta, 
                ingrediente_id=ingrediente_id
            )
            receta_ingrediente.delete()
            return JsonResponse({'success': True})
        except RecetaIngrediente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ingrediente no encontrado'})
    
    return JsonResponse({'success': False})


@login_required
def crear_receta(request):
    if request.method == 'POST':
        form = FormularioReceta(request.POST, request.FILES)
        ingrediente_formset = RecetaIngredienteFormSet(request.POST, prefix='ingredientes')
        if form.is_valid() and ingrediente_formset.is_valid():
            try:
                with transaction.atomic(): 
                    receta = form.save(commit=False)
                    receta.creado_por = request.user 
                    receta.save() 
                    ingrediente_formset.instance = receta
                    ingrediente_formset.save()

                messages.success(request, '¡Receta y sus ingredientes creados exitosamente!')
                return redirect('detalle_receta', receta_id=receta.id) 
            except Exception as e:
                messages.error(request, f'Ocurrió un error al guardar la receta o los ingredientes: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario de la receta o en los ingredientes.')
    else:
        form = FormularioReceta()
        ingrediente_formset = RecetaIngredienteFormSet(prefix='ingredientes')

    context = {
        'form': form,
        'ingrediente_formset': ingrediente_formset,
    }
    return render(request, 'recetas/crear_receta.html', context)
@login_required
def toggle_favorito(request, receta_id):
    if request.method == 'POST':
        receta = get_object_or_404(Receta, id=receta_id)
        favorito, created = Favorito.objects.get_or_create(
            usuario=request.user,
            receta=receta
        )
        if not created:
            favorito.delete()
            es_favorito = False
        else:
            es_favorito = True
        return JsonResponse({'es_favorito': es_favorito})
    else:
        return HttpResponseForbidden("Método no permitido.")
@login_required
def mis_favoritos(request):
    
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('receta')
    context = {
        'favoritos': favoritos,
        'title': 'Mis Recetas Favoritas',
    }
    return render(request, 'recetas/mis_favoritos.html', context)

def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'recetas/lista_usuarios.html', {'usuarios': usuarios})

def lista_ingredientes(request):
    ingredientes = Ingrediente.objects.all()
    return render(request, 'recetas/lista_ingredientes.html', {'ingredientes': ingredientes})

@login_required
def crear_ingrediente(request):
    if request.method == 'POST':
        form = FormularioIngrediente(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente creado exitosamente.')
            return redirect('lista_ingredientes')
    else:
        form = FormularioIngrediente()
    return render(request, 'recetas/crear_ingrediente.html', {'form': form})

@login_required
def quitar_favorito(request, receta_id):
    """
    Elimina una receta de la lista de favoritos del usuario.
    """
    if request.method == 'POST': 
        receta = get_object_or_404(Receta, pk=receta_id)
        try:
            favorito = Favorito.objects.get(usuario=request.user, receta=receta)
            favorito.delete()
            messages.success(request, f'"{receta.nombre}" ha sido eliminada de tus favoritos.')
        except Favorito.DoesNotExist:
            messages.warning(request, f'"{receta.nombre}" no estaba en tus favoritos.')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al quitar la receta de favoritos: {e}')
    return redirect('mis_favoritos')
