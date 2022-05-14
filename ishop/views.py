import os
import urllib
from operator import attrgetter
from urllib.request import urlretrieve

import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.files import File
from django.core.paginator import Paginator, PageNotAnInteger
from django.shortcuts import render, HttpResponse, redirect
from .models import City, Client, Buy, Step, Buy_step, Category, Product, Buy_product, Author, Genre, Books, \
    Oilproducer, Motoroils, Motoroilsvolums, Commentsbook
from django.db.models import Q, Count
from itertools import chain
from .form import UserRegForm, UserAuthForm, CommBookForm ,ClientForm


def CreateAvatar(model, name):
    try:
        image, _ = urlretrieve(f'http://localhost:8080/monster/{name}')
    except urllib.error.URLError:
        image = False
    if image:
        model.clientPhoto = File(open(image, 'rb'), name=f'{name}.img')
        model.save()

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
        filte = sorted(chain(books, oils), key=attrgetter('prod.id'), reverse=True)[:9]
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
            login(request, user)
            messages.success(request, f', {user.username}, you are logged in')
            return redirect('/')
    category = Category.objects.values_list('categoryName', flat=True)
    authform = UserAuthForm()
    return render(request, 'login.html', {'authform': authform, 'category': category})


def registerPage(request):
    if request.method == 'POST':
        regform = UserRegForm(request.POST)
        if regform.is_valid():
            user = regform.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f', {user.username}, you are registered ')
            return redirect('/')
    else:
        regform = UserRegForm()
    category = Category.objects.values_list('categoryName', flat=True)
    param = {
        'regform': regform,
        'category': category,
    }
    return render(request, 'registration.html', param)


def pagecategory(request, category):
    cats = Category.objects.all()

    if category == 'books':

        genres = Genre.objects.annotate(num_books=Count('books')).order_by('-num_books')
        authors = Author.objects.annotate(num_books=Count('books')).order_by('-num_books')
        filter = {
            'search': False,
            'author': False,
            'genre': False,
            'res': False,
            'MIN': False,
            'MAX': False,
            'authorother': False,
            'genreother': False,
        }
        if request.method == "POST":
            filter['res'] = True
            if request.POST.get('search', None):
                books = Books.objects.filter(booksTitle__icontains=request.POST['search'])
                filter['search'] = request.POST.get('search', None)
            if request.POST.getlist('author'):
                filter['author'] = Author.objects.filter(authorName__in=request.POST.getlist('author'))
                filter['authorother'] = Author.objects.exclude(authorName__in=request.POST.getlist('author'))

                try:
                    books = books.filter(booksAuthor__authorName__in=request.POST.getlist('author'))
                except NameError:
                    books = Books.objects.filter(booksAuthor__authorName__in=request.POST.getlist('author'))

            if request.POST.getlist('genre'):
                filter['genre'] = Genre.objects.filter(genreName__in=request.POST.getlist('genre'))
                filter['genreother'] = Genre.objects.exclude(genreName__in=request.POST.getlist('genre'))
                print(request.POST.getlist('genre'))
                try:
                    books = books.filter(booksGenre__genreName__in=request.POST.getlist('genre'))
                except NameError:
                    books = Books.objects.filter(booksGenre__genreName__in=request.POST.getlist('genre'))
                print(books.count(), 7777777)

            if request.POST.getlist('MIN') and request.POST.getlist('MAX'):
                filter['MIN'] = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else False
                filter['MAX'] = int(request.POST.get('MAX')) if request.POST.get('MAX', None) else False
                min = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else 0
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



        else:
            books = Books.objects.all().order_by('-prod_id')
        countorders = 6
        if filter['res']:
            countorders = 100
            print(100)
        pagbook = Paginator(books, countorders)
        pageNum = request.GET.get('page')
        if pageNum:
            try:
                get_page = pagbook.page(pageNum)
            except PageNotAnInteger:
                get_page = pagbook.page(1)
        else:
            get_page = pagbook.page(1)
        param = {
            'cats': cats,
            'books': get_page,
            'genres': genres,
            'authors': authors,
            'filter': filter,
        }
        return render(request, 'books.html', param)
    return HttpResponse('books')


def pagegenre(request, pk):
    cats = Category.objects.all()
    try:
        genre = Genre.objects.get(pk=pk)
    except Genre.DoesNotExist:
        genre = False
    books = Books.objects.filter(booksGenre__pk=pk)
    authors = Author.objects.filter(books__booksGenre__genreName=genre).annotate(num_books=Count('books')).order_by(
        '-num_books')
    filter = {
        'search': False,
        'author': False,
        'res': False,
        'MIN': False,
        'MAX': False,
        'authorother': False,
    }
    if request.method == "POST":
        filter['res'] = True
        if request.POST.get('search', None):
            books = books.filter(
                Q(booksTitle__icontains=request.POST['search']) |
                Q(booksAuthor__authorName__icontains=request.POST['search'])
            )
            filter['search'] = request.POST.get('search', None)
        if request.POST.getlist('author'):
            filter['author'] = authors.filter(authorName__in=request.POST.getlist('author'))
            filter['authorother'] = Author.objects.exclude(authorName__in=request.POST.getlist('author'))
            books = books.filter(booksAuthor__authorName__in=request.POST.getlist('author'))

        if request.POST.getlist('MIN') and request.POST.getlist('MAX'):
            filter['MIN'] = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else False
            filter['MAX'] = int(request.POST.get('MAX')) if request.POST.get('MAX', None) else False
            min = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else 0
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

    pagbook = Paginator(books, 10)
    pageNum = request.GET.get('page')
    if pageNum:
        try:
            get_page = pagbook.page(pageNum)
        except PageNotAnInteger:
            get_page = pagbook.page(1)
    else:
        get_page = pagbook.page(1)
    param = {
        'cats': cats,
        'books': get_page,
        'genre': genre,
        'authors': authors,
        'filter': filter,
    }
    return render(request, 'booksgenre.html', param)


def book(request, genr, boo):
    cats = Category.objects.all()
    book = Books.objects.get(pk=boo)

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommBookForm(data=request.POST)
        if form.is_valid():
            formsave = form.save(commit=False)
            formsave.combookBooks_id = boo
            formsave.combookUser = request.user
            formsave.save()

    form = CommBookForm()
    comments = book.comment.all().order_by('-combookDate')
    for i in comments:
        i.timebefore = i.time_before()
    pagbook = Paginator(comments, 10)
    pageNum = request.GET.get('page')
    if pageNum:
        try:
            get_page = pagbook.page(pageNum)
        except PageNotAnInteger:
            get_page = pagbook.page(1)
    else:
        get_page = pagbook.page(1)

    param = {
        'cats': cats,
        'book': book,
        'form': form,
        'comments': get_page
    }
    return render(request, 'book.html', param)


def removecomment(request, genr, boo, comm):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            comment = Books.objects.get(pk=boo).comment.get(pk=comm)
            comment.delete()
            messages.success(request, 'Comment has been removed')
        except (Commentsbook.DoesNotExist,Books.DoesNotExist):
            messages.warning(request, "Can't delete comment")
        return redirect(f'/category/books/{genr}/{boo}')


def profile(request, name):
    cats = Category.objects.all()


    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.pk)
        try:
            clien = user.client
            if not clien.clientPhoto:
                CreateAvatar(clien, name)
            if not clien.clientEmail:
                clien.clientEmail = user.email
                clien.save()
        except User.client.RelatedObjectDoesNotExist:
            try:
                image, _ = urlretrieve(f'http://localhost:8080/monster/{name}')
            except urllib.error.URLError:
                image = False
            clien = Client.objects.create(
                    clientUser=user,
                    slug=user.username,
                )
            if image:
                clien.clientPhoto=File(open(image, 'rb'), file=image)
            if user.email:
                clien.clientEmail = user.email
            clien.save()
        if request.method == 'POST':
            cform = ClientForm(request.POST, request.FILES, instance=clien)
            print(request.POST.get('clientPhoto-clear'),123)
            if cform.is_valid():
                print(request.POST)
                if request.POST.get('clientPhoto-clear'):
                    cform = cform.save(commit=False)
                    cform.clientPhoto.delete()
                    CreateAvatar(clien, name)
                    cform.save()
                else:
                    cform.save()
        cform = ClientForm(instance=clien)

        param = {
            'cats': cats,
            'client':clien,
            'cform': cform,
        }
    return render(request,'profile.html', param)

def test(request):
    return HttpResponse('OK')
