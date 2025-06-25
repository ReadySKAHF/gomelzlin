# apps/company/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class AboutView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>О компании</h1><p>В разработке...</p>')

class LeadershipView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Руководство</h1><p>В разработке...</p>')

class PartnersView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Партнеры</h1><p>В разработке...</p>')

class PoliciesView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Политики компании</h1><p>В разработке...</p>')