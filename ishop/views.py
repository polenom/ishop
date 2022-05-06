from operator import attrgetter

from django.contrib.auth import login
from django.shortcuts import render, HttpResponse, redirect
from .models import City, Client, Buy, Step, Buy_step, Category, Product, Buy_product, Author, Genre, Books, \
    Oilproducer, Motoroils, Motoroilsvolums
from django.db.models import Q
from itertools import chain
from .form import UserRegForm, UserAuthForm


# Create your views here.

def startpage(request):
    category = Category.objects.values_list('categoryName', flat=True)
    newOrder = Product.objects.all().order_by('-id')[:12]
    print(newOrder)
    filte = False
    if request.method == 'POST':
        namefilter = request.POST['q']
        print(namefilter, 777777777777)
        print()
        books = Books.objects.filter(
            Q(booksTitle__icontains=namefilter) |
            Q(booksAuthor__authorName__icontains=namefilter) |
            Q(booksGenre__genreName__icontains=namefilter)
        )
        oils = Motoroils.objects.filter(
            Q(motoroilsTitle__icontains=namefilter)
        )
        filte = sorted(chain(books, oils), key=attrgetter('prod.id'), reverse=True)
    params = {
        'category': category,
        'filte': filte,
        'newOrder': newOrder
    }
    return render(request, 'index.html', params)


def loginPage(request):
    if request.method == "POST":
        authform = UserAuthForm(data=request.POST)
        print(123)
        print(request.POST)
        print(authform.is_valid())
        if authform.is_valid():
            user = authform.get_user()
            print(user)
            login(request,user)
            return redirect('/')
    category = Category.objects.values_list('categoryName', flat=True)
    authform = UserAuthForm()
    return render(request,'login.html', {'authform': authform, 'category':category})


def registerPage(request):
    return HttpResponse('register')


def pagecategory(request, category):
    return HttpResponse('Ok')


def test(request):
    return HttpResponse('OK')
