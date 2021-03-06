# -*- coding: utf-8 -*-

# Project: "EmprendeNet"
# Script: main.py - App handler mapping
# App identifier: emprende-net
# URL: www.---.com
# Author: Marcos Manuel Ortega - Indavelopers
# Version: v1.0 - 12/2015


# -- Imports --
import os
import webapp2
import jinja2


# Initialize Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# -- Handlers --
class MainHandler(webapp2.RequestHandler):
	def render(self, template, params=None):
		if not params:
			params = {}

		t = jinja_env.get_template(template)

		self.response.out.write(t.render(params))


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


class Error404(MainHandler):
	def get(self):
		self.error(404)

		self.render('error-404.html')
