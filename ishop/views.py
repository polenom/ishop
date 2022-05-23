import os
import urllib
from operator import attrgetter
from urllib.request import urlretrieve

import pytz as pytz
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
from .form import UserRegForm, UserAuthForm, CommBookForm, ClientForm, CommOilForm, CountForm


def CreateAvatar(model, name):
    try:
        image, _ = urlretrieve(f'http://localhost:8080/monster/{name}')
    except urllib.error.URLError:
        image = False
    if image:
        model.clientPhoto = File(open(image, 'rb'), name=f'{name}.img')
        model.save()


class Cart:

    def __init__(self, request):
        self.request = request
        self.sesson = request.session
        cart = self.sesson.get('cart')
        if not cart:
            cart = self.sesson['cart'] = {}
        self.cart = cart

    def add(self, product, value, count=1):
        if value != '-1':
            price = Motoroils.objects.get(pk=product).oilvolume.get(motoroilsvolumsVolums=value)
            if price.motoroilsvolumsPrice:
                self.cart[str(product) + '/' + value] = {'value': value, 'count': count,
                                                         'price': price.motoroilsvolumsPrice}
            else:
                messages.error(self.request, 'The product is out of stock')
        else:
            price = Books.objects.get(pk=product)
            if price.booksPrice:
                self.cart[str(product) + '/' + value] = {'value': value, 'count': count,
                                                         'price': price.booksPrice}
            else:
                messages.error(self.request, 'The product is out of stock')
            print(self.cart, 'booook')

    def delete(self, product, value):
        del self.cart[str(product) + '/' + value]
        self.save()

    def clear(self):
        del self.sesson['cart']
        self.sesson.modified = True

    def get_total_price(self):
        print([i for i in self.cart.values()])
        return str(round(sum([i['price'] * int(i['count']) for i in self.cart.values()]), 2))

    def save(self):
        self.sesson['cart'] = self.cart
        self.sesson.modified = True

    def __len__(self):
        return sum([int(item['count']) for item in self.cart.values()])

    def __iter__(self):
        for prod in self.cart.keys():
            self.cart[prod]['summa'] = str(round(self.cart[prod]['price'] * int(self.cart[prod]['count']), 2))
            if prod.split('/')[-1] != '-1':
                self.cart[prod]['product'] = Motoroils.objects.get(pk=prod.split('/')[0]).oilvolume.get(
                    motoroilsvolumsVolums=prod.split('/')[-1])
                print(self.cart[prod])
                yield self.cart[prod]
            else:
                self.cart[prod]['product'] = Books.objects.get(pk=prod.split('/')[0])
                yield self.cart[prod]

    # if request.session.get('cart'):
    #     res = []
    #     for tovar in request.session.keys():
    #         try:
    #             pr = int(tovar)
    #         except ValueError:
    #             continue
    #         if request.session[tovar]['type'] == 1:
    #             res.append((Motoroils.objects.get(pk=pr).oilvolume.get(motoroilsvolumsVolums=float(request.session[tovar]['value'])),request.session[tovar]['count']))
    #         else:
    #             pass
    #     print(request.session.keys(),1111)
    #     print(res)
    #     return res


# Create your views here.

def startpage(request):
    category = Category.objects.values_list('categoryName', flat=True)
    newOrder = Product.objects.all().order_by('-id')[:12]
    filte = False
    if request.method == 'POST':
        namefilter = request.POST['q']
        books = Books.objects.filter(
            Q(booksTitle__icontains=namefilter) |
            Q(booksAuthor__authorName__icontains=namefilter) |
            Q(booksGenre__genreName__icontains=namefilter)
        )
        oils = Motoroils.objects.filter(
            Q(motoroilsTitle__icontains=namefilter)
        )
        filte = sorted(chain(books, oils), key=attrgetter('prod.id'), reverse=True)[:9]
    cart = Cart(request)
    params = {
        'category': category,
        'filte': filte,
        'newOrder': newOrder,
        'cart': cart,
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
    cart = Cart(request)
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
                books = Books.objects.filter(Q(booksTitle__icontains=request.POST['search']) |
                                             Q(booksAuthor__authorName__icontains=request.POST['search']))
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
            'cart': cart,
        }
        return render(request, 'books.html', param)
    if category == 'oils':

        volums = Motoroilsvolums.objects.values_list('motoroilsvolumsVolums', flat=True).distinct(
            'motoroilsvolumsVolums').order_by('motoroilsvolumsVolums')
        volums = [str(num) for num in volums]
        filter = {
            'res': False,
            'search': False,
            'MIN': False,
            'MAX': False,
            'oil': False,
            'volum': False,
        }
        oils = False
        if request.method == "POST":
            filter['res'] = True
            if request.POST.get('search', None):
                oils = Motoroils.objects.filter(motoroilsTitle__icontains=request.POST['search'])
                filter['search'] = request.POST.get('search')
            if request.POST.get('oil', None):
                filter['oil'] = request.POST.getlist('oil')

                if oils != False:
                    oils = oils.filter(motoroilsProducer__oilproducer__in=request.POST.getlist('oil')).distinct()
                else:
                    oils = Motoroils.objects.filter(
                        motoroilsProducer__oilproducer__in=request.POST.getlist('oil')).distinct()
            if request.POST.get('MAX', None) or request.POST.get('MIN', None) or request.POST.get('volum', None):
                filter['MAX'] = int(request.POST.get('MAX')) if request.POST.get('MAX', None) else False
                filter['MIN'] = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else False
                min = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else 0
                max = int(request.POST.get('MAX')) if request.POST.get('MAX', None) else 100000000000000000
                if oils:
                    if request.POST.get('volum', None):
                        filter['volum'] = request.POST.getlist('volum')
                        oils = oils.filter(
                            Q(oilvolume__motoroilsvolumsPrice__lte=max) &
                            Q(oilvolume__motoroilsvolumsPrice__gte=min) &
                            Q(oilvolume__motoroilsvolumsVolums__in=request.POST.getlist('volum'))
                        )
                    else:
                        oils = oils.filter(
                            Q(oilvolume__motoroilsvolumsPrice__lte=max) &
                            Q(oilvolume__motoroilsvolumsPrice__gte=min)
                        )
                else:
                    if request.POST.get('volum', None):
                        filter['volum'] = request.POST.getlist('volum')
                        oils = Motoroils.objects.filter(
                            Q(oilvolume__motoroilsvolumsPrice__lte=max) &
                            Q(oilvolume__motoroilsvolumsPrice__gte=min) &
                            Q(oilvolume__motoroilsvolumsVolums__in=request.POST.getlist('volum'))
                        )
                    else:
                        oils = Motoroils.objects.filter(
                            Q(oilvolume__motoroilsvolumsPrice__lte=max) &
                            Q(oilvolume__motoroilsvolumsPrice__gte=min)
                        )
            if filter['oil']:
                oilproducer5 = Oilproducer.objects.filter(oilproducer__in=filter['oil'])
                oilproducerO = Oilproducer.objects.exclude(oilproducer__in=filter['oil']).annotate(
                    num_oils=Count('oils')).order_by('-num_oils')
            oils = oils.distinct()
        else:
            oils = Motoroils.objects.all().order_by('-prod_id')
        if not filter['res']:
            get_page = Paginator(oils, 10)
            pageNum = request.GET.get('page')
            if pageNum:
                try:
                    oils = get_page.page(pageNum)
                except PageNotAnInteger:
                    oils = get_page.page(1)
            else:
                oils = get_page.page(1)
        if not filter['oil']:
            oilproducer = Oilproducer.objects.annotate(num_oils=Count('oils')).order_by('-num_oils')
            oilproducer5 = oilproducer[:5]
            oilproducerO = oilproducer[5:]
        param = {
            'cats': cats,
            'filter': filter,
            'oilproducer5': oilproducer5,
            'oilproducerO': oilproducerO,
            'volums': volums,
            'oils': oils,
            'cart': cart,
        }
        return render(request, 'oils.html', param)
    return HttpResponse('books')


def pageoilproducer(request, pk):
    cats = Category.objects.all()
    cart = Cart(request)
    try:
        producer = Oilproducer.objects.get(pk=pk)
    except Oilproducer.DoesNotExist:
        producer = False

    filter = {
        'res': False,
        'search': False,
        'MIN': False,
        'MAX': False,
        'volum': False,
    }

    if request.method == "POST":
        filter['res'] = True
        oils = Motoroils.objects.filter(motoroilsProducer=pk)
        if request.POST.get('search', None):
            oils = Motoroils.objects.filter(motoroilsTitle__icontains=request.POST['search'])
            filter['search'] = request.POST.get('search')
        if request.POST.get('MAX', None) or request.POST.get('MIN', None) or request.POST.get('volum', None):
            filter['MAX'] = int(request.POST.get('MAX')) if request.POST.get('MAX', None) else False
            filter['MIN'] = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else False
            min = int(request.POST.get('MIN')) if request.POST.get('MIN', None) else 0
            max = int(request.POST.get('MAX')) if request.POST.get('MAX', None) else 100000000000000000
            print(request.POST.getlist('volum', None), 777)
            if request.POST.get('volum', None):
                filter['volum'] = request.POST.getlist('volum')
                print(request.POST.getlist('volum', None), 777)
                oils = oils.filter(
                    Q(oilvolume__motoroilsvolumsPrice__lte=max) &
                    Q(oilvolume__motoroilsvolumsPrice__gte=min) &
                    Q(oilvolume__motoroilsvolumsVolums__in=request.POST.getlist('volum'))
                )
            else:
                oils = oils.filter(
                    Q(oilvolume__motoroilsvolumsPrice__lte=max) &
                    Q(oilvolume__motoroilsvolumsPrice__gte=min)
                )
        oils = oils.distinct()
    else:
        oils = Motoroils.objects.filter(motoroilsProducer=pk)
    volums = Motoroilsvolums.objects.filter(motoroilsvolums__motoroilsProducer=pk).values_list('motoroilsvolumsVolums',
                                                                                               flat=True).distinct().order_by(
        'motoroilsvolumsVolums')
    volums = [str(num) for num in volums]
    param = {
        'cats': cats,
        'producer': producer,
        'oils': oils,
        'volums': volums,
        'filter': filter,
        'cart': cart,

    }

    return render(request, 'oilsproducer.html', param)


def pagegenre(request, pk):
    cats = Category.objects.all()
    cart = Cart(request)
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
        'cart': cart,
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
        'cart': cart,
    }
    return render(request, 'booksgenre.html', param)


def oil(request, pk, pr):
    cats = Category.objects.all()
    oil = Motoroils.objects.get(pk=pr)

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommOilForm(data=request.POST)
        if form.is_valid():
            formsave = form.save(commit=False)
            formsave.comoilOil_id = pr
            formsave.comoilUser = request.user
            formsave.save()
    form = CommOilForm()
    comments = oil.commentOil.all().order_by('-comoilDate')
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
    formadd = CountForm()
    cart = Cart(request)

    param = {
        'cats': cats,
        'oil': oil,
        'form': form,
        'formadd': formadd,
        'comments': get_page,
        'cart': cart,
    }
    return render(request, 'oil.html', param)


def book(request, genr, boo):
    cats = Category.objects.all()
    book = Books.objects.get(pk=boo)
    cart = Cart(request)

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
    formadd = CountForm()
    param = {
        'cats': cats,
        'book': book,
        'form': form,
        'comments': get_page,
        'formadd': formadd,
        'cart': cart,
    }
    return render(request, 'book.html', param)


def removecomment(request, genr, boo, comm):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            comment = Books.objects.get(pk=boo).comment.get(pk=comm)
            comment.delete()
            messages.success(request, 'Comment has been removed')
        except (Commentsbook.DoesNotExist, Books.DoesNotExist):
            messages.warning(request, "Can't delete comment")
        return redirect(f'/category/books/{genr}/{boo}')


def profile(request, name):
    cats = Category.objects.all()
    cart = Cart(request)
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
            clien = Client.objects.create(
                clientUser=user,
                slug=user.username,
            )
            CreateAvatar(clien, name)
            if user.email:
                clien.clientEmail = user.email
            clien.save()
        if request.method == 'POST':
            cform = ClientForm(request.POST, request.FILES, instance=clien)

            if cform.is_valid():
                cform = cform.save(commit=False)
                if request.POST.get('clientPhoto-clear'):
                    cform.clientPhoto.delete()
                    CreateAvatar(clien, name)
                    cform.save()
                if request.POST.get('country'):
                    try:
                        county = City.objects.get(cityName=request.POST.get('country'))
                    except City.DoesNotExist:
                        county = City.objects.create(cityName=request.POST.get('country'))
                    cform.clientCountry = county
                cform.save()
        cform = ClientForm(instance=clien)

        param = {
            'cats': cats,
            'client': clien,
            'cform': cform,
            'cart': cart,
        }

    return render(request, 'profile.html', param)


def test(request):
    return HttpResponse('OK')


def oiladd(request, pk, pr):
    cart = Cart(request)
    print(request.session['cart'], 'valuesssssssssss')
    cart.add(
        product=pr,
        value=request.GET['val'],
        count=request.POST.get('quantity')
    )
    cart.save()

    if request.GET['val'] != '-1':
        return redirect(f'/category/oils/{pk}/{pr}/')
    else:
        return redirect(f'/category/books/{pk}/{pr}/')


def deletemycartitem(request, pk, val):
    cart = Cart(request)
    cart.delete(product=pk, value=val)
    return redirect('/cart/')


def cartclear(request):
    cart=Cart(request)
    cart.clear()
    return redirect('/cart/')


def mycart(request):
    cart = Cart(request)
    cats = Category.objects.all()
    param = {
        'carts': cart,
        'cats': cats,
    }
    return render(request, 'cart.html', param)
