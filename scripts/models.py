# -*- coding: utf-8 -*-

# Project: "EmprendeNet"
# Script: models.py - Datastore models
# App identifier: emprende-net
# URL: www.---.com
# Author: Marcos Manuel Ortega - Indavelopers
# Version: v2.0 - 12/2015


# -- Imports --
import random
import string
import hashlib

from scripts.globals import *
from scripts.config import *

from google.appengine.ext import ndb


# -- Models --
def model_key(model, name='default'):
	""" Genera una key para usar como ancestro con el modelo Usuario

	Argumentos:
	- model (str) - Modelo
	- name (str, default = 'default') - Grupo de usuarios

	Devuelve:
	- key (Key) - Con modelo Usuario e ID "name"
	"""
	return ndb.Key(model, name)


class Usuario(ndb.Model):
	""" Modelo Usuario, modela todo usuario de la aplicación, incluidos usuarios con roles

	Métodos:
	- comprobar_permiso - Comprueba si el usuario tiene permiso para realizar la acción indicada
	- validar_usuario - Valida la información de usuario para loguearlo, registrarlo, cambiar su contraseña o editar su
	 perfil
	- login_user - Actualiza recordar usuario si debe
	- register_user - Registra usuario
	- editar_usuario - Edita la información de usuario según la acción a editar
	- eliminar_usuario - Elimina el usuario
	- generate_user_salt - Genera un salt aleatorio para el usuario
	- generate_password_hash - Genera el hash del password para el usuario
	- generate_user_cookie_hash - Genera el hash correspondiente a la cookie "usuario" del usuario
	- get_user_by_id - Recupera usuario según ID
	- get_user_by_name - Recupera usuario según nombre
	"""
	nombre = ndb.StringProperty()
	salt = ndb.StringProperty()
	password_hash = ndb.StringProperty()
	recordar = ndb.BooleanProperty()
	rol = ndb.StringProperty(default='usuario')
	fecha_registro = ndb.DateTimeProperty(auto_now_add=True)

	def comprobar_permiso(self, accion):
		"""Comprueba si dicho usuario tiene permisos para realizar la acción dada

		Argumentos:
		- accion (str) - Acción a confirmar
		- elemento (obj, default = None) - Elemento sobre el que se realiza la acción

		Devuelve:
		- True/False (bool) - El usuario tiene permiso necesario o no
		- None - Accion inválida

		Eleva:
		- TypeError - Accion no es string
		"""
		try:
			assert isinstance(accion, str)

		except AssertionError:
			raise TypeError('Accion a realizar no es "str"')

		if accion == 'panel-admin':
			return self.rol == 'admin'

		else:
			return None

	@classmethod
	def validar_usuario(cls, params, accion):
		"""Valida la información de usuario para loguear, registrarlo, cambiar su contraseña o editar su perfil

		Argumentos:
		- params (dict) - Parámetros para editar el usuario
		- accion (str) - Acción a editar

		Devuelve:
		- mensaje de error (str) - Parámetros inválidos
		- True (bool) - Parámetros válidos
		"""
		if accion == 'login' or accion == 'registrar':
			if not validate_value(params['nombre_usuario'], 'usuario_nombre') and \
					not validate_value(params['password'], 'usuario_password'):
				return 'Nombre de usuario y contrase&ntilde;a inv&aacute;lidos.'

			if not validate_value(params['nombre_usuario'], 'usuario_nombre'):
				return 'Nombre de usuario inv&aacute;lido.'

			if not validate_value(params['password'], 'usuario_password'):
				return 'Contrase&ntilde;a inv&aacute;lida.'

		if accion == 'login':
			usuario = Usuario.get_user_by_name(params['nombre_usuario'])
			if not usuario:
				return 'Usuario inexistente.'

			if usuario.password_hash != usuario.generate_password_hash(params['password']):
				return 'Contrase&ntilde;a incorrecta.'

		elif accion == 'registrar':
			usuario = Usuario.get_user_by_name(params['nombre_usuario'])
			if usuario:
				return 'Nombre de usuario ya en uso.'

		elif accion == 'cambiar_password':
			if not validate_value(params['password_anterior'], 'usuario_password'):
				return 'Contrase&ntilde;a anterior inv&aacute;lida.'

			if not validate_value(params['password_nueva'], 'usuario_password'):
				return 'Nueva contrase&ntilde;a inv&aacute;lida.'

			if not validate_value(params['password_confirmar'], 'usuario_password'):
				return 'Confirmar nueva contrase&ntilde;a introducida inv&aacute;lida.'

			if params['password_nueva'] != params['password_confirmar']:
				return 'Nueva contrase&ntilde;a y confirmar nueva contrase&ntilde;a no coinciden.'

			if params['usuario'].password_hash != params['usuario'].generate_password_hash(params['password_anterior']):
				return 'Contrase&ntilde;a anterior incorrecta.'

		elif accion == 'editar_perfil':
			pass    # todo

		return True

	def login_user(self, remmember):
		"""Recupera usuario y actualiza su estado de recordar sesión si debe

		Argumentos:
		- usuario (instance Usuario) - Usuario
		- remmember (bool) - Recordar

		Devuelve:
		- usuario (instance Usuario) - Usuario
		"""
		if not self.recordar and remmember:
			self.recordar = True

			self.put()

			mc.set('usuario-nombre={}'.format(self.nombre), self)

	@classmethod
	def register_user(cls, user_name, user_password, remmember):
		"""Registra usuario

		Argumentos:
		- user_name (str) - Nombre de usuario
		- user_password (str) - Contraseña
		- remmember (bool) - Recordar

		Devuelve:
		- usuario (instance) - Usuario ya registrado
		"""
		usuario = Usuario(parent=model_key(Usuario),
						  nombre=user_name,
						  salt=cls.generate_user_salt(),
						  recordar=remmember)
		usuario.password_hash = usuario.generate_password_hash(user_password)

		usuario.put()

		mc.set('usuario-nombre={}'.format(usuario.nombre), usuario)

		return usuario

	def editar_usuario(self, params, accion):
		"""Edita el usuario según los parámetros de edición y la acción a editar

		Argumentos:
		- usuario (instance Usuario) - Usuario a editar
		- params (dict) - Parámetros de edición
		- accion (str) - Acción a editar
		"""
		if accion == 'editar_perfil':
			pass    # todo

		elif accion == 'cambiar_password':
			self.password_hash = self.generate_password_hash(params['password_nueva'])

		self.put()

		mc.set('usuario-nombre={}'.format(self.nombre), self)

	def eliminar_usuario(self):
		"""Elimina el usuario

		Argumentos:
		- usuario (instance Usuario) - Usuario a eliminar
		"""
		self.key.delete()

		flush_mc('usuario-nombre={}'.format(self.nombre))

	@staticmethod
	def generate_user_salt():
		"""Genera salt única para usuario, 16 caracteres alfanuméricos (minúsculas y mayúsculas) aleatorios

		Devuelve:
		- salt (str) - 16 caracteres alfanuméricos
		"""
		return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
					   for _ in xrange(16))

	def generate_password_hash(self, password):
		""" Genera hash correspondiente a la contraseña del usuario

		Argumentos:
		- password (str) - Contraseña
		- user_salt (str) - Salt del usuario

		Devuelve:
		- hash (str) - Hash en formato hexadecimal
		"""
		return hashlib.sha256('password_hash' + self.salt + password + SALT3 + SALT4).hexdigest()

	def generate_user_cookie_hash(self):
		""" Genera hash correspondiente a la cookie "usuario" para el usuario

		Argumentos:
		- user (instance) - Usuario

		Devuelve:
		- hash (str) - Hash en hexadecimal
		"""
		hash_ = hashlib.sha256('cookie_usuario' + str(self.key.id()) + self.password_hash + SALT1 + SALT2)

		return hash_.hexdigest()

	@classmethod
	def get_user_by_id(cls, user_id):
		""" Recupera usuario según ID

		Argumentos:
		- user_id (Key.id()) - ID del usuario

		Devuelve:
		- False (bool) - ID del usuario incorrecta
		- usuario (instance Usuario) - Usuario deseado
		- None (bool) - Usuario inexistente
		"""
		if not validate_value(user_id, 'instancia_id'):
			return False

		usuario = Usuario.get_by_id(long(user_id), parent=model_key(Usuario))

		return usuario

	@classmethod
	def get_user_by_name(cls, user_name):
		""" Recupera usuario según nombre

		Argumentos:
		- user_name (str) - Nombre del usuario

		Devuelve:
		- False (bool) - ID del usuario incorrecta
		- usuario (instance Usuario) - Existe usuario
		- None (bool) - Usuario inexistente
		"""
		if not validate_value(user_name, "usuario_nombre"):
			return False

		usuario = mc.get('usuario-nombre={}'.format(user_name))
		if not usuario:
			q_u = cls.query(cls.nombre == user_name, ancestor=model_key(Usuario))
			usuario = q_u.get()

			mc.set('usuario-nombre={}'.format(user_name), usuario)

		return usuario
