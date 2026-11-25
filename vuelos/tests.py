from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from vuelos.models import Aerolinea, Pasajero, Reserva, Vuelo


class BaseTest(TestCase):
    def setUp(self):
        self.admins = Group.objects.get(name='administradores')
        self.consultores = Group.objects.get(name='consultores')
        self.admin = User.objects.create_user('adm', password='clave12345')
        self.admin.groups.add(self.admins)
        self.cons1 = User.objects.create_user('cons1', password='clave12345')
        self.cons1.groups.add(self.consultores)
        self.cons2 = User.objects.create_user('cons2', password='clave12345')
        self.cons2.groups.add(self.consultores)
        self.aerolinea = Aerolinea.objects.create(nombre='LATAM', codigo_iata='LA', pais='Chile')
        salida = timezone.now() + timedelta(days=5)
        self.vuelo = Vuelo.objects.create(
            codigo='LA100', aerolinea=self.aerolinea, origen='Quito', destino='Lima',
            fecha_salida=salida, fecha_llegada=salida + timedelta(hours=3),
            precio=Decimal('150.00'), asientos=10,
        )
        self.pasajero = Pasajero.objects.create(
            nombres='Ana', apellidos='Gomez', documento='1712345678',
            email='ana@example.com', fecha_nacimiento=date(1995, 1, 1),
            creado_por=self.cons1,
        )
        self.pasajero_ajeno = Pasajero.objects.create(
            nombres='Luis', apellidos='Perez', documento='1798765432',
            email='luis@example.com', fecha_nacimiento=date(1990, 5, 5),
            creado_por=self.cons2,
        )
        self.reserva = Reserva.objects.create(
            codigo='RSV-T1', vuelo=self.vuelo, total=Decimal('150.00'), creado_por=self.cons1,
        )
        self.reserva.pasajeros.add(self.pasajero)


class ModeloTests(BaseTest):
    def test_str_y_url(self):
        self.assertIn('LATAM', str(self.aerolinea))
        self.assertEqual(self.reserva.get_absolute_url(), reverse('reserva_detail', args=[self.reserva.pk]))

    def test_relaciones_en_ambos_sentidos(self):
        self.assertIn(self.vuelo, self.aerolinea.vuelos.all())
        self.assertIn(self.reserva, self.pasajero.reservas.all())
        self.assertIn(self.pasajero, self.reserva.pasajeros.all())

    def test_asientos_disponibles(self):
        self.assertEqual(self.vuelo.asientos_disponibles, 9)

    def test_grupos_creados_por_codigo(self):
        self.assertTrue(self.admins.permissions.filter(codename='delete_vuelo').exists())
        self.assertFalse(self.consultores.permissions.filter(codename='delete_vuelo').exists())
        self.assertTrue(self.consultores.permissions.filter(codename='add_reserva').exists())
        self.assertTrue(self.consultores.permissions.filter(codename='add_pasajero').exists())


class AutenticacionTests(BaseTest):
    def test_anonimo_va_al_login(self):
        respuesta = self.client.get(reverse('reserva_create'))
        self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse('reserva_create')}")

    def test_anonimo_no_ve_listados(self):
        respuesta = self.client.get(reverse('vuelo_list'))
        self.assertEqual(respuesta.status_code, 302)

    def test_registro_crea_usuario_consultor(self):
        respuesta = self.client.post(reverse('registro'), {
            'username': 'nuevo', 'email': 'nuevo@example.com',
            'nombres': 'Marta', 'apellidos': 'Rios', 'documento': 'PA998877',
            'fecha_nacimiento': '1992-03-04',
            'password1': 'ClaveSegura2026*', 'password2': 'ClaveSegura2026*',
        })
        self.assertRedirects(respuesta, reverse('login'))
        usuario = User.objects.get(username='nuevo')
        self.assertTrue(usuario.groups.filter(name='consultores').exists())
        pasajero = Pasajero.objects.get(documento='PA998877')
        self.assertEqual(pasajero.creado_por, usuario)
        self.assertEqual(pasajero.email, 'nuevo@example.com')

    def test_logout_solo_por_post(self):
        self.client.login(username='adm', password='clave12345')
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        respuesta = self.client.post(reverse('logout'))
        self.assertRedirects(respuesta, reverse('login'))


class PermisosTests(BaseTest):
    def test_consultor_no_puede_crear_vuelo(self):
        self.client.login(username='cons1', password='clave12345')
        self.assertEqual(self.client.get(reverse('vuelo_create')).status_code, 403)

    def test_consultor_no_ve_botones_de_administrador(self):
        self.client.login(username='cons1', password='clave12345')
        respuesta = self.client.get(reverse('vuelo_list'))
        self.assertNotContains(respuesta, reverse('vuelo_create'))
        self.assertNotContains(respuesta, reverse('vuelo_update', args=[self.vuelo.pk]))

    def test_administrador_ve_botones(self):
        self.client.login(username='adm', password='clave12345')
        respuesta = self.client.get(reverse('vuelo_list'))
        self.assertContains(respuesta, reverse('vuelo_create'))

    def test_consultor_edita_su_reserva(self):
        self.client.login(username='cons1', password='clave12345')
        self.assertEqual(self.client.get(reverse('reserva_update', args=[self.reserva.pk])).status_code, 200)

    def test_otro_consultor_no_edita_reserva_ajena(self):
        self.client.login(username='cons2', password='clave12345')
        self.assertEqual(self.client.get(reverse('reserva_update', args=[self.reserva.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('reserva_delete', args=[self.reserva.pk])).status_code, 403)
        self.assertTrue(Reserva.objects.filter(pk=self.reserva.pk).exists())

    def test_administrador_edita_cualquier_reserva(self):
        self.client.login(username='adm', password='clave12345')
        self.assertEqual(self.client.get(reverse('reserva_update', args=[self.reserva.pk])).status_code, 200)


class CrudTests(BaseTest):
    def test_id_inexistente_da_404(self):
        self.client.login(username='adm', password='clave12345')
        for nombre in ('reserva_detail', 'reserva_update', 'reserva_delete', 'vuelo_detail', 'aerolinea_update'):
            self.assertEqual(self.client.get(reverse(nombre, args=[9999])).status_code, 404, nombre)

    def test_crear_reserva_con_mensaje_y_autor(self):
        self.client.login(username='cons2', password='clave12345')
        respuesta = self.client.post(reverse('reserva_create'), {
            'codigo': 'rsv-nueva', 'vuelo': self.vuelo.pk, 'pasajeros': [self.pasajero_ajeno.pk],
            'clase': 'ECO', 'estado': 'PEN', 'fecha_reserva': date.today().isoformat(),
        }, follow=True)
        reserva = Reserva.objects.get(codigo='RSV-NUEVA')
        self.assertEqual(reserva.creado_por, self.cons2)
        self.assertContains(respuesta, 'Reserva creada exitosamente.')
        self.assertEqual(reserva.total, self.vuelo.precio)

    def test_total_se_calcula_por_pasajeros_y_clase(self):
        self.client.login(username='cons1', password='clave12345')
        self.client.post(reverse('reserva_create'), {
            'codigo': 'rsv-calc', 'vuelo': self.vuelo.pk, 'pasajeros': [self.pasajero.pk],
            'clase': 'EJE', 'estado': 'PEN', 'fecha_reserva': date.today().isoformat(),
            'total': '1.00',
        })
        reserva = Reserva.objects.get(codigo='RSV-CALC')
        self.assertEqual(reserva.total, Reserva.calcular_total(self.vuelo, 'EJE', 1))
        self.assertNotEqual(reserva.total, Decimal('1.00'))

    def test_borrado_pide_confirmacion_y_solo_elimina_por_post(self):
        self.client.login(username='cons1', password='clave12345')
        respuesta = self.client.get(reverse('reserva_delete', args=[self.reserva.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Reserva.objects.filter(pk=self.reserva.pk).exists())
        respuesta = self.client.post(reverse('reserva_delete', args=[self.reserva.pk]), follow=True)
        self.assertFalse(Reserva.objects.filter(pk=self.reserva.pk).exists())
        self.assertContains(respuesta, 'Reserva eliminada exitosamente.')

    def test_no_elimina_aerolinea_con_vuelos(self):
        self.client.login(username='adm', password='clave12345')
        respuesta = self.client.post(reverse('aerolinea_delete', args=[self.aerolinea.pk]), follow=True)
        self.assertTrue(Aerolinea.objects.filter(pk=self.aerolinea.pk).exists())
        self.assertContains(respuesta, 'No se puede eliminar')

    def test_validacion_vuelo_llegada_posterior(self):
        self.client.login(username='adm', password='clave12345')
        respuesta = self.client.post(reverse('vuelo_create'), {
            'codigo': 'xx1', 'aerolinea': self.aerolinea.pk, 'origen': 'Quito', 'destino': 'Quito',
            'fecha_salida': '2030-01-02T10:00', 'fecha_llegada': '2030-01-02T09:00',
            'precio': '100', 'asientos': '50', 'estado': 'PRG',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Vuelo.objects.filter(codigo='XX1').exists())


class PasajerosPorUsuarioTests(BaseTest):
    def test_consultor_solo_ve_sus_pasajeros_en_el_listado(self):
        self.client.login(username='cons1', password='clave12345')
        respuesta = self.client.get(reverse('pasajero_list'))
        self.assertContains(respuesta, 'Gomez')
        self.assertNotContains(respuesta, 'Perez')

    def test_administrador_ve_todos_los_pasajeros(self):
        self.client.login(username='adm', password='clave12345')
        respuesta = self.client.get(reverse('pasajero_list'))
        self.assertContains(respuesta, 'Gomez')
        self.assertContains(respuesta, 'Perez')

    def test_formulario_de_reserva_solo_ofrece_pasajeros_propios(self):
        self.client.login(username='cons1', password='clave12345')
        respuesta = self.client.get(reverse('reserva_create'))
        self.assertContains(respuesta, 'Gomez')
        self.assertNotContains(respuesta, 'Perez')

    def test_no_puede_reservar_con_pasajero_ajeno(self):
        self.client.login(username='cons1', password='clave12345')
        respuesta = self.client.post(reverse('reserva_create'), {
            'codigo': 'rsv-x', 'vuelo': self.vuelo.pk, 'pasajeros': [self.pasajero_ajeno.pk],
            'clase': 'ECO', 'estado': 'PEN', 'fecha_reserva': date.today().isoformat(),
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Reserva.objects.filter(codigo='RSV-X').exists())

    def test_pasajero_ajeno_da_404_para_consultor(self):
        self.client.login(username='cons1', password='clave12345')
        for nombre in ('pasajero_detail', 'pasajero_update', 'pasajero_delete'):
            self.assertEqual(self.client.get(reverse(nombre, args=[self.pasajero_ajeno.pk])).status_code, 404, nombre)

    def test_consultor_registra_pasajero_y_queda_como_dueno(self):
        self.client.login(username='cons1', password='clave12345')
        respuesta = self.client.post(reverse('pasajero_create'), {
            'nombres': 'Marta', 'apellidos': 'Rios', 'documento': 'PA123456',
            'email': 'marta@example.com', 'fecha_nacimiento': '1992-03-04', 'nacionalidad': 'Ecuatoriana',
        }, follow=True)
        pasajero = Pasajero.objects.get(documento='PA123456')
        self.assertEqual(pasajero.creado_por, self.cons1)
        self.assertContains(respuesta, 'Pasajero creado exitosamente.')

    def test_consultor_edita_y_elimina_su_pasajero(self):
        self.client.login(username='cons1', password='clave12345')
        self.assertEqual(self.client.get(reverse('pasajero_update', args=[self.pasajero.pk])).status_code, 200)
        self.client.post(reverse('pasajero_delete', args=[self.pasajero.pk]))
        self.assertFalse(Pasajero.objects.filter(pk=self.pasajero.pk).exists())

    def test_registro_con_documento_repetido_no_crea_usuario(self):
        respuesta = self.client.post(reverse('registro'), {
            'username': 'otro', 'email': 'otro@example.com',
            'nombres': 'Ana', 'apellidos': 'Gomez', 'documento': '1712345678',
            'fecha_nacimiento': '1992-03-04',
            'password1': 'ClaveSegura2026*', 'password2': 'ClaveSegura2026*',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username='otro').exists())

    def test_cliente_nuevo_ve_su_pasajero_marcado_al_reservar(self):
        self.client.post(reverse('registro'), {
            'username': 'cliente', 'email': 'cliente@example.com',
            'nombres': 'Marta', 'apellidos': 'Rios', 'documento': 'PA112233',
            'fecha_nacimiento': '1992-03-04',
            'password1': 'ClaveSegura2026*', 'password2': 'ClaveSegura2026*',
        })
        self.client.login(username='cliente', password='ClaveSegura2026*')
        respuesta = self.client.get(reverse('reserva_create'))
        propio = Pasajero.objects.get(documento='PA112233')
        self.assertContains(respuesta, 'Rios')
        self.assertNotContains(respuesta, 'Gomez')
        self.assertContains(respuesta, 'value="%s" id="id_pasajeros_0" checked' % propio.pk)
        self.assertContains(respuesta, 'id="total-estimado"')
        self.assertContains(respuesta, 'id="datos-total"')