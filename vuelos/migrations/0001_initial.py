import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Aerolinea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('codigo_iata', models.CharField(max_length=3, unique=True)),
                ('pais', models.CharField(max_length=60)),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'aerolínea',
                'verbose_name_plural': 'aerolíneas',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Pasajero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombres', models.CharField(max_length=80)),
                ('apellidos', models.CharField(max_length=80)),
                ('documento', models.CharField(max_length=20, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('fecha_nacimiento', models.DateField()),
                ('nacionalidad', models.CharField(default='Ecuatoriana', max_length=60)),
            ],
            options={
                'verbose_name': 'pasajero',
                'verbose_name_plural': 'pasajeros',
                'ordering': ['apellidos', 'nombres'],
            },
        ),
        migrations.CreateModel(
            name='Vuelo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10, unique=True)),
                ('origen', models.CharField(max_length=80)),
                ('destino', models.CharField(max_length=80)),
                ('fecha_salida', models.DateTimeField()),
                ('fecha_llegada', models.DateTimeField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8)),
                ('asientos', models.PositiveIntegerField(default=150)),
                ('estado', models.CharField(choices=[('PRG', 'Programado'), ('RET', 'Retrasado'), ('CAN', 'Cancelado'), ('COM', 'Completado')], default='PRG', max_length=3)),
                ('aerolinea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vuelos', to='vuelos.aerolinea')),
            ],
            options={
                'verbose_name': 'vuelo',
                'verbose_name_plural': 'vuelos',
                'ordering': ['fecha_salida'],
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=12, unique=True)),
                ('clase', models.CharField(choices=[('ECO', 'Económica'), ('EJE', 'Ejecutiva'), ('PRI', 'Primera clase')], default='ECO', max_length=3)),
                ('estado', models.CharField(choices=[('PEN', 'Pendiente'), ('CON', 'Confirmada'), ('CAN', 'Cancelada')], default='PEN', max_length=3)),
                ('fecha_reserva', models.DateField(default=django.utils.timezone.localdate)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reservas_creadas', to=settings.AUTH_USER_MODEL)),
                ('pasajeros', models.ManyToManyField(related_name='reservas', to='vuelos.pasajero')),
                ('vuelo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservas', to='vuelos.vuelo')),
            ],
            options={
                'verbose_name': 'reserva',
                'verbose_name_plural': 'reservas',
                'ordering': ['-fecha_reserva', '-id'],
            },
        ),
    ]
