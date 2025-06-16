from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuario' 
urlpatterns = [
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'), 
    path('logout/', views.logout_usuario, name='logout'), 
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('perfil/configuracion/', views.configuracion_cuenta, name='configuracion'),
    path('perfil/desactivar/', views.desactivar_cuenta, name='desactivar_cuenta'),
    path('usuario/<str:username>/', views.perfil_publico, name='perfil_publico'),
    path('lista/', views.lista_usuarios, name='lista_usuarios'), 
    path('ajax/verificar-usuario/', views.ajax_verificar_usuario, name='ajax_verificar_usuario'),
    path('mi-perfil/', views.mi_perfil_con_gestion_recetas, name='mi_perfil_con_gestion_recetas'),
]