# -*- coding: utf-8 -*-

# Project: "EmprendeNet"
# Script: main.py - App handler mapping
# App identifier: emprende-net
# URL: www.---.com
# Author: Marcos Manuel Ortega - Indavelopers
# Version: v1.0 - 12/2015


# -- Imports --
import webapp2

from scripts.handlers import *


# -- App --
app = webapp2.WSGIApplication([('/', StaticPage),
                               ('/mas-informacion', StaticPage),
                               ('/el-equipo', StaticPage),
                               ('/aviso-legal', StaticPage),
                               ('/webmap', Webmap)],
                              debug=True)
