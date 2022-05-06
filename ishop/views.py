from operator import attrgetter

from django.contrib import messages
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
        if authform.is_valid():
            user = authform.get_user()
            login(request,user)
            messages.success(request, f', {user.username}, you are logged in')
            return redirect('/')
    category = Category.objects.values_list('categoryName', flat=True)
    authform = UserAuthForm()
    return render(request,'login.html', {'authform': authform, 'category':category})


def registerPage(request):
    if request.method == 'POST':
        regform = UserRegForm(request.POST)
        if regform.is_valid():
            user = regform.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request,f', {user.username}, you are registered ')
            return redirect('/')
    else:
        regform = UserRegForm()
    category = Category.objects.values_list('categoryName', flat=True)
    param = {
        'regform':regform,
        'category':category,
    }
    return render(request, 'registration.html', param )


def pagecategory(request, category):
    cats = Category.objects.values_list('categoryName', flat=True)

    if category == 'books':
        books = Books.objects.all().order_by('-prod_id')
        param = {
            'cats': cats,
            'books':books
        }
        return render(request, 'books.html', param)
    return HttpResponse('books')


def test(request):
    return HttpResponse('OK')
