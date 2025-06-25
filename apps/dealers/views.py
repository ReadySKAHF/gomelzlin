# apps/dealers/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class DealerListView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Дилерские центры</h1><p>В разработке...</p>')

class DealerDetailView(TemplateView):
    def get(self, request, pk):
        return HttpResponse(f'<h1>Дилер: {pk}</h1><p>В разработке...</p>')