from django.shortcuts import render, HttpResponse
from .models import City, Client, Buy, Step, Buy_step, Category, Product, Buy_product, Author, Genre, Books, \
    Oilproducer, Motoroils, Motoroilsvolums
# Create your views here.

def startpage(request):
    category = Category.objects.values_list('categoryName', flat=True)
    params = {
        'category': category
    }
    return render(request, 'index.html',params)

def pagecategory(request, category):

    return HttpResponse('Ok')


def test(request):
    return HttpResponse('OK')