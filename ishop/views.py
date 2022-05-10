from operator import attrgetter

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, HttpResponse, redirect
from .models import City, Client, Buy, Step, Buy_step, Category, Product, Buy_product, Author, Genre, Books, \
    Oilproducer, Motoroils, Motoroilsvolums
from django.db.models import Q, Count
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
    cats = Category.objects.all()

    if category == 'books':

        genres = Genre.objects.annotate(num_books=Count('books')).order_by('-num_books')
        authors = Author.objects.annotate(num_books=Count('books')).order_by('-num_books')

        if request.method == "POST":
            if request.POST.get('search', None):
                books = Books.objects.filter(booksTitle__icontains=request.POST['search'])
            if request.POST.getlist('author'):
                try:
                    books = books.filter(booksAuthor__authorName__in=request.POST.getlist('author'))
                except NameError:
                    books = Books.objects.filter(booksAuthor__authorName__in=request.POST.getlist('author'))
            if request.POST.getlist('genre'):
                try:
                    books = books.filter(booksGenre__genreName__in=request.POST.getlist('genre'))
                except NameError:
                    books = Books.objects.filter(booksGenre__genreName__in=request.POST.getlist('genre'))
            if request.POST.getlist('MIN') and request.POST.getlist('MAX'):
                print(request.POST.get('MIN'), ' ============== ', request.POST.get('MAX'))
                min =int(request.POST.get('MIN')) if request.POST.get('MIN', None) else 0
                max = int(request.POST.get('MAX')) if request.POST.get('MAX', None) else 100000000000000000
                try:
                    books = books.filter(
                        Q(booksPrice__lte=max) &
                        Q(booksPrice__gte=min)
                    )
                except NameError:
                    books = Books.objects.filter(
                        Q(booksPrice__lte=max) &
                        Q(booksPrice__gte=min)
                    )

            print(request.POST.getlist('genre'))
            print(request.POST)
            print(books,123)
        else:
            books = Books.objects.all().order_by('-prod_id')
        param = {
            'cats': cats,
            'books': books,
            'genres': genres,
            'authors': authors,
        }
        return render(request, 'books.html', param)
    return HttpResponse('books')


def test(request):
    return HttpResponse('OK')
