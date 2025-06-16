

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Receta, Ingrediente, RecetaIngrediente, Usuario

from django.forms import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML

class FormularioRegistroUsuario(UserCreationForm):
    nombre_usuario = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = User
        
        
        fields = ('username', 'email') 
        

    
    
    
    
    
    

class FormularioReceta(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['nombre', 'descripcion', 'categoria', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
class FormularioIngrediente(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nombre']
class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['nombre', 'descripcion', 'categoria', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la receta'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción de la receta'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control-file'
            })
        }

class RecetaIngredienteForm(forms.ModelForm):
    class Meta:
        model = RecetaIngrediente
        fields = ['ingrediente', 'cantidad']
        widgets = {
            'ingrediente': forms.Select(attrs={
                'class': 'form-control ingrediente-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingrediente'].queryset = Ingrediente.objects.all()
        self.fields['ingrediente'].empty_label = "Seleccionar ingrediente"


RecetaIngredienteFormSet = inlineformset_factory(
    Receta, 
    RecetaIngrediente,
    form=RecetaIngredienteForm,
    extra=1, 
    can_delete=True,
    min_num=1,  
    validate_min=True
)

class FormularioBusqueda(forms.Form):
    ingrediente = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por ingrediente',
            'class': 'form-control'
        })
    )
