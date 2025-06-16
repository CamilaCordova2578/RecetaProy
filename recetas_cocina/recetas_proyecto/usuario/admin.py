from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil 
class PerfilInline(admin.StackedInline): 
    model = Perfil 
    can_delete = False 
    verbose_name_plural = 'Perfil de Usuario' 
    fields = (
        'foto_perfil',
        'descripcion', 
        'fecha_nacimiento',
    )

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,) 
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active', 
        'is_staff',
        'get_descripcion_corta', 
        'get_fecha_nacimiento_perfil', 
    )

    list_filter = BaseUserAdmin.list_filter + (
    )

    def get_descripcion_corta(self, obj):
        
        if hasattr(obj, 'perfil') and obj.perfil.descripcion:
            return obj.perfil.descripcion[:50] + '...' if len(obj.perfil.descripcion) > 50 else obj.perfil.descripcion
        return '-'
    get_descripcion_corta.short_description = 'Descripción de Perfil'

    def get_fecha_nacimiento_perfil(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil.fecha_nacimiento:
            return obj.perfil.fecha_nacimiento
        return '-'
    get_fecha_nacimiento_perfil.short_description = 'Fecha Nacimiento'

@admin.register(Perfil) 
class PerfilAdmin(admin.ModelAdmin): 
    list_display = (
        'usuario_username', 
        'get_nombre_completo_usuario', 
        'descripcion', 
        'fecha_nacimiento',
        'foto_perfil_thumbnail', 
    )

    list_filter = (
        'fecha_nacimiento',
    )


    search_fields = (
        'usuario__username', 
        'usuario__first_name',
        'usuario__last_name',
        'descripcion',
    )

    readonly_fields = (
    )

    fieldsets = (
        ('Información Básica del Perfil', {
            'fields': ('usuario', 'foto_perfil', 'descripcion', 'fecha_nacimiento',)
        }),
    )

    def usuario_username(self, obj):
        return obj.usuario.username
    usuario_username.short_description = 'Usuario (Login)'
    usuario_username.admin_order_field = 'usuario__username' 

    def get_nombre_completo_usuario(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}" if obj.usuario.first_name or obj.usuario.last_name else obj.usuario.username
    get_nombre_completo_usuario.short_description = 'Nombre Completo User'

    def foto_perfil_thumbnail(self, obj):
        from django.utils.html import mark_safe
        if obj.foto_perfil:
            return mark_safe(f'<img src="{obj.foto_perfil.url}" width="50" height="50" style="border-radius: 50%;" />')
        return '-'
    foto_perfil_thumbnail.short_description = 'Miniatura'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
