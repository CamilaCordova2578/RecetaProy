

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recetas', '0002_remove_receta_imagenes_receta_imagen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingrediente',
            name='unidad_medida',
        ),
    ]
