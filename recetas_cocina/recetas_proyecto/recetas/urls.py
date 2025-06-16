from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='recetas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    path('recetas/', views.lista_recetas, name='lista_recetas'),
    path('recetas/<int:receta_id>/', views.detalle_receta, name='detalle_receta'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('recetas/<int:receta_id>/editar/', views.editar_receta, name='editar_receta'),
    path('recetas/crear/', views.crear_receta, name='crear_receta'),
    path('recetas/<int:receta_id>/favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('quitar_favorito/<int:receta_id>/', views.quitar_favorito, name='quitar_favorito'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('ingredientes/', views.lista_ingredientes, name='lista_ingredientes'),
    path('ingredientes/crear/', views.crear_ingrediente, name='crear_ingrediente'),
    path('receta/<int:receta_id>/editar/', views.editar_receta, name='editar_receta'),
    path('ajax/agregar-ingrediente/', views.agregar_ingrediente_ajax, name='agregar_ingrediente_ajax'),
    path('receta/<int:receta_id>/eliminar-ingrediente/<int:ingrediente_id>/', 
         views.eliminar_ingrediente_receta, name='eliminar_ingrediente_receta'),
    path('buscar/', views.buscador_global, name='buscador_global'),
    path('ajax/sugerencias/', views.sugerencias_ajax, name='sugerencias_ajax'),
    
]