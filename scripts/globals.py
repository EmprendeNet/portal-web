# -*- coding: utf-8 -*-

# Project: "EmprendeNet"
# Script: globals.py - Global vars and functions
# App identifier: emprende-net
# URL: www.---.com
# Author: Marcos Manuel Ortega - Indavelopers
# Version: v2.0 - 12/2015


# -- Imports --
import re

from google.appengine.api import memcache as mc


# -- Global variables --
# Duración de la sesión del usuario en horas
TIEMPO_SESION = 0.5
TIEMPO_SESION_MAX = 365 * 24

# Número de elementos por página
LONGITUD_PAGINA = 30

# Código para transmitir mensaje a mostrar
CODIGO_MENSAJE = {'ulog': 'Usuario ya logueado.',
                  'unlo': 'Sesi&oacute;n no iniciada.',
                  'logo': 'Sesi&oacute;n cerrada.',
                  'logi': 'Debes iniciar sesi&oacute;n antes.',
                  'uinc': 'Usuario incorrecto.',
                  'perd': 'Perfil editado correctamente.',
                  'cone': 'Contrase&ntilde;a cambiada con &eacute;xito.',
                  'usel': 'Usuario eliminado.',
                  'caex': 'Cambios realizados con &eacute;xito.',
                  'npem': 'No tienes permisos para editar este mensaje.'}


# -- Global functions
def validate_value(value, value_type):
    """ Recibe un valor y tipo de valor y lo valida contra unas reglas predeterminadas

    Argumentos:
    - value (str)- Valor a validar
    - value_type (str) - Tipo de valor a validar

    Devuelve:
    - True (bool) - Valor correcto según tipo de valor
    - False (bool) - Valor incorrecto o False
    - None (bool) - Valor None
    """
    if type(value) is bool or value is None:
        return value

    elif type(value) is str:
        value = unicode(value, 'utf-8')

    else:
        value = unicode(value)

    if value_type == 'usuario_nombre':
        if value == 'Usuario desconocido' or value == 'Admin':
            return False

    regex_dict = {'instancia_id': ur'^\d{1,16}$',
                  'usuario_nombre': ur'^[\w -]{4,20}$',
                  'usuario_password': ur'^[\w!@"#$%&\\/()=?¡\+[\]{}<>ºª€·,.;:_-]{4,20}$',
                  'usuario_info': ur'^[\w,.;: -]{2,20}$'}

    regex = re.compile(regex_dict[value_type], re.UNICODE)

    return True if regex.match(value) else False


def flush_mc(keys=None):
    """ Elimina keys de MC

    Argumentos:
    - keys (Key|list (Keys)|None (default = None)) - Keys a eliminar de la MC

    Eleva:
    - TypeError - Tipo de keys inválido
    """
    try:
        assert type(keys) is str or type(keys) is list or keys is None

    except AssertionError:
        raise TypeError('Tipo de "keys" inválido')

    max_retries = 50

    if type(keys) is str:
        for _ in xrange(max_retries):
            if mc.delete(keys):
                break

        else:
            return False

    elif type(keys) is list:
        for _ in xrange(max_retries):
            if mc.delete_multi(keys):
                break

        else:
            return False

    else:
        for _ in xrange(max_retries):
            if mc.flush_all():
                break

        else:
            return False

    return True
