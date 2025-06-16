from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm 
from django.contrib.auth import get_user_model 
from django.core.exceptions import ValidationError 
from .models import Perfil 
User = get_user_model()

class FormularioRegistro(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Usuario para iniciar sesión (único)'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        
        if commit:
            user.save()
            Perfil.objects.create(usuario=user, descripcion="Hola, soy un nuevo usuario.")
        return user

class FormularioLogin(AuthenticationForm):
    """Formulario personalizado para login"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Usuario o Email' 
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })


class FormularioEditarPerfil(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, required=False, label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        max_length=30, required=False, label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )

    class Meta:
        model = Perfil 
        fields = [
            'foto_perfil',
            'descripcion',
            'fecha_nacimiento',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Cuéntanos sobre ti...'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.usuario: 
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['last_name'].initial = self.instance.usuario.last_name
            self.fields['email'].initial = self.instance.usuario.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_instance = self.instance.usuario
        if User.objects.filter(email=email).exclude(pk=user_instance.pk).exists():
            raise ValidationError("Este email ya está registrado por otro usuario.")
        return email

    def save(self, commit=True):
        perfil = super().save(commit=False) 
        user = perfil.usuario 
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save() 
            perfil.save() 
        return perfil


class FormularioCambiarContrasena(forms.Form):
    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        }),
        label='Contraseña actual'
    )
    
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        label='Nueva contraseña',
        min_length=8, 
        help_text='Mínimo 8 caracteres. Debe incluir letras mayúsculas, minúsculas, números y símbolos.'
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label='Confirmar nueva contraseña'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_contrasena_actual(self):
        contrasena_actual = self.cleaned_data.get('contrasena_actual')
        if not self.user.check_password(contrasena_actual):
            raise ValidationError("La contraseña actual es incorrecta.")
        return contrasena_actual

    def clean(self):
        cleaned_data = super().clean()
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')

        if nueva_contrasena and confirmar_contrasena: 
            if nueva_contrasena != confirmar_contrasena:
                raise ValidationError("Las nuevas contraseñas no coinciden.")    
        return cleaned_data

    def save(self):
        nueva_contrasena = self.cleaned_data['nueva_contrasena']
        self.user.set_password(nueva_contrasena) 
        self.user.save() 
        return self.user
