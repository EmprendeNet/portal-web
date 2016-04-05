# -*- coding: utf-8 -*-

# Project: "EmprendeNet"
# Script: handlers.py - App handler mapping
# App identifier: emprende-net
# URL: www.---.com
# Author: Marcos Manuel Ortega - Indavelopers
# Version: v2.0 - 12/2015


# -- Imports --
import os
import webapp2
import jinja2
import datetime
import urllib
from scripts.models import *
from scripts.globals import *


# Initialize Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# -- Handlers --
class MainHandler(webapp2.RequestHandler):
	""" Handler ancestro con los principales métodos

	Métodos:
	- get_cookie - Recupera cookie
	- set_cookie - Establece cookie con expiración deseada
	- check_user_cookie - Recupera ID de usuario logueado o False, renueva cookie de sesión si no recordar usuario
	- login - Loguea al usuario
	- logout - Desloguea al usuario
	- render_page - Recupera plantilla y rellena con valores comunes y parámetros necesarios
	- render - Recupera plantilla y la rellena según parámetros
	- initialize - Inicializa sesión del usuario
	"""

	def get_cookie(self, name):
		""" Recupera cookie según su nombre

		Argumentos:
		- name (str) - Nombre de la cookie

		Devuelve:
		- cookie (str) - Valor de la cookie
		"""
		return self.request.cookies.get(name)

	def set_cookie(self, name, value, expiration=TIEMPO_SESION_MAX):
		""" Establece la cookie con expiración indicada en horas o nunca (1 año)

		Argumentos:
		- name (str) - Nombre de la cookie
		- value (str) - Valor a establecer
		- expiration (int|str, default = 'never') - Horas hasta expiración o 1 año (por defecto)
		"""
		expira = datetime.datetime.now() + datetime.timedelta(hours=expiration)

		self.response.set_cookie(name, value, expires=expira, path='/')

	def check_user_cookie(self):
		""" Comprueba la cookie "usuario" y devuelve ID de usuario, None si no logueado o False si usuario inválido

		Devuelve:
		- None (bool) - No existe cookie "usuario" o es incorrecta
		- False (bool) - Usuario inexistente o hash inválido
		- id (Key.id()) - Existe usuario
		"""
		cookie = self.get_cookie('usuario')
		if not cookie or '|' not in cookie:
			return None

		usuario_id = cookie.split('|')[0]
		usuario_cookie_hash = cookie.split('|')[1]

		usuario = Usuario.get_user_by_id(usuario_id)
		if not usuario or not usuario_cookie_hash == usuario.generate_user_cookie_hash():
			return False

		if not usuario.recordar:
			self.set_cookie('usuario', usuario_id + '|' + usuario_cookie_hash, TIEMPO_SESION)

		return usuario.key.id()

	def login(self, user):
		""" Loguea al usuario y establece su cookie hasta tiempo de sesión o nunca si recordar

		Argumentos:
		- user (instancia Usuario) - Usuario
		"""
		self.usuario = user.key.id()

		expirar = TIEMPO_SESION_MAX if user.recordar else TIEMPO_SESION
		self.set_cookie('usuario', str(user.key.id()) + '|' + user.generate_user_cookie_hash(), expirar)

	def logout(self):
		""" Vacía la cookie "usuario" y la hace expirar, vacía self.usuario
		"""
		self.set_cookie('usuario', '', 0)

		self.usuario = None

	def render_page(self, template, params=None):
		""" Recupera plantilla, rellena con valores comunes a todas las páginas y con los parámetros especificados

		Argumentos:
		- template (str) - Plantilla a usar
		- params (dict, default = None) - Parámetros a rellenar en la plantilla
		"""
		if not params:
			params = {}

		m = self.request.get('m')

		usuario = Usuario.get_user_by_id(self.usuario)

		params['path'] = urllib.quote(self.request.path)
		params['mensaje'] = CODIGO_MENSAJE.get(m)
		params['usuario_nombre'] = usuario.nombre if usuario else False

		self.render(template, params)

	def render(self, template, params=None):
		""" Recupera plantilla y rellena con los parámetros indicados

		Argumentos:
		- template (str) - Plantilla a recuperar
		- params (dict, default = None) - Parámetros a rellenar
		"""
		if not params:
			params = {}

		t = jinja_env.get_template(template)

		self.response.out.write(t.render(params))

	def initialize(self, *a, **kw):
		""" Inicializa la petición y establece la sesión del usuario

		Argumentos:
		- a - Arguments
		- kw - Keywords
		"""
		webapp2.RequestHandler.initialize(self, *a, **kw)

		self.usuario = self.check_user_cookie()


class StaticPage(MainHandler):
	def get(self):
		templates = {'': 'inicio.html',
		             'mas-informacion': 'mas-informacion.html',
		             'el-equipo': 'el-equipo.html',
		             'aviso-legal': 'aviso-legal.html'}

		page = self.request.path.split('/')[-1]

		try:
			template = templates[page]

		except KeyError:
			template = 'error-404.html'

		self.render(template)


class Webmap(MainHandler):
	def get(self):
		base_url = 'http://www.---.com/'

		urls = ['', 'aviso-legal']

		sitemap = [base_url + u for u in urls]

		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(sitemap)


class IniciarSesionRegistro(MainHandler):
	def get(self):
		path = self.request.get('p') or '/'

		if self.usuario:
			self.redirect(path + '?m=ulog', abort=True)

		self.render_page('iniciar-sesion-registro.html')

	def post(self):
		path = self.request.get('p') or '/'

		if self.usuario:
			self.redirect(path + '?m=ulog', abort=True)

		nombre_usuario = self.request.get('nombre_usuario')
		password = self.request.get('password')
		recordar = self.request.get('recordar') == 'recordar'
		registrar = self.request.get('registrar') == 'registrar'

		params = {'nombre_usuario': nombre_usuario,
		          'password': password,
		          'recordar': recordar,
		          'registrar': registrar}

		error = ''

		if registrar:
			res = Usuario.validar_usuario(params, accion='registrar')

			if res is not True:
				error = res
			else:
				usuario = Usuario.register_user(nombre_usuario, password, recordar)

				path = '/usuario/{}/perfil/editar'.format(usuario.key.id())

		else:
			res = Usuario.validar_usuario(params, accion='login')

			if res is not True:
				error = res
			else:
				usuario = Usuario.get_user_by_name(nombre_usuario)

				usuario.login_user(recordar)

		if error:
			params = {'nombre_usuario': nombre_usuario,
			          'password': password,
			          'recordar': self.request.get('recordar'),
			          'registrar': self.request.get('registrar'),
			          'path': path,
			          'error': error}

			self.render_page('iniciar-sesion-registro.html', params)
		else:
			self.login(usuario)

			self.redirect(path)


class CerrarSesion(MainHandler):
	def get(self):
		if self.usuario:
			self.usuario = False

			self.logout()

			m = 'logo'
		else:
			m = 'unlo'

		self.redirect('/' + '?m={}'.format(m))


class PerfilUsuario(MainHandler):
	def get(self, usuario_id):
		usuario = Usuario.get_user_by_id(usuario_id)

		if not usuario:
			params = {'error': 'Usuario no encontrado.'}

			self.error(404)
		else:
			propio_usuario = self.usuario == long(usuario_id)

			params = {'usuario': usuario,
			          'usuario_id': self.usuario if propio_usuario else None,
			          'propio_usuario': propio_usuario,
			          'acceder_panel_admin': usuario.comprobar_permiso('panel-admin')}

		self.render_page('perfil.html', params)


class PerfilUsuarioEditar(MainHandler):
	def get(self, usuario_id):
		if not self.usuario:
			self.redirect('/iniciar-sesion-registro' + '?m={}&p={}'.format('logi', self.request.path), abort=True)

		elif self.usuario != long(usuario_id):
			self.redirect('/usuario/{}/perfil?m={}'.format(usuario_id, 'uinc'), abort=True)

		usuario = Usuario.get_user_by_id(usuario_id)

		params = {}

		self.render_page('perfil-editar.html', params)

	def post(self, usuario_id):
		if not self.usuario:
			self.redirect('/iniciar-sesion-registro' + '?m={}&p={}'.format('logi', self.request.path), abort=True)

		elif self.usuario != long(usuario_id):
			self.redirect('/usuario/{}/perfil' + '?m={}'.format(usuario_id, 'uinc'), abort=True)

		# todo params

		params = {}

		error = ''

		res = Usuario.validar_usuario(params, accion='editar_perfil')
		if res is not True:
			error = res

		usuario = Usuario.get_user_by_id(usuario_id)

		if error:
			params = {}

			self.render_page('perfil-editar.html', params)

		else:
			usuario.editar_usuario(params, accion='editar_perfil')

			self.redirect('/usuario/{}/perfil?m={}'.format(usuario_id, 'perd'))


class PanelUsuario(MainHandler):
	def get(self):
		usuario = Usuario.get_user_by_id(self.usuario)

		if not usuario:
			self.redirect('/iniciar-sesion-registro' + '?m={}&p={}'.format('logi', self.request.path), abort=True)

		params = {'usuario_id': self.usuario,
		          'acceder_panel_admin': usuario.comprobar_permiso('panel-admin')}

		self.render_page('panel-usuario.html', params)


class CambiarPasswordUsuario(MainHandler):
	def get(self):
		if not self.usuario:
			self.redirect('/iniciar-sesion-registro' + '?m={}&p={}'.format('logi', self.request.path), abort=True)

		self.render_page('cambiar-password.html')

	def post(self):
		if not self.usuario:
			self.redirect('/iniciar-sesion-registro' + '?m={}&p={}'.format('logi', self.request.path), abort=True)

		password_anterior = self.request.get('password_anterior')
		password_nueva = self.request.get('password_nueva')
		password_confirmar = self.request.get('password_confirmar')

		error = ''

		user_params = {'password_anterior': password_anterior,
		               'password_nueva': password_nueva,
		               'password_confirmar': password_confirmar,
		               'usuario': Usuario.get_user_by_id(self.usuario)}

		res = Usuario.validar_usuario(user_params, accion='cambiar_password')
		if res is not True:
			error = res

		if error:
			params = {'error': error}

			self.render_page('cambiar-password.html', params)

		else:
			usuario = Usuario.get_user_by_id(self.usuario)

			usuario.editar_usuario(user_params, accion='cambiar_password')

			self.login(usuario)

			self.redirect('/usuario/panel-usuario?m={}'.format('cone'))


class EliminarUsuario(MainHandler):
	def get(self):
		if not self.usuario:
			self.redirect('/iniciar-sesion-registro' + '?m={}&p={}'.format('logi', self.request.path), abort=True)

		self.render_page('eliminar-usuario.html')

	def post(self):
		if not self.usuario:
			self.redirect('/iniciar-sesion-registro' + '?m={}&p={}'.format('logi', self.request.path), abort=True)

		confirmar = self.request.POST.get('confirmar') == 'confirmar'

		if not confirmar:
			self.redirect('/usuario/panel-usuario', abort=True)

		usuario = Usuario.get_user_by_id(self.usuario)

		usuario.eliminar_usuario()

		self.logout()

		self.redirect('/?m={}'.format('usel'))


class Error404(MainHandler):
	def get(self):
		self.error(404)

		self.render('error-404.html')
