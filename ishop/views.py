import os
import urllib
from datetime import datetime, timezone, timedelta
from operator import attrgetter
from urllib.request import urlretrieve
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.files import File
from django.core.paginator import Paginator, PageNotAnInteger
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import City, Client, Buy, Step, Buy_step, Category, Product, Buy_product, Author, Genre, Books, \
    Oilproducer, Motoroils, Motoroilsvolums, Commentsbook, CheckEmail, Commentsoil, ReplyComOil, ReplyReplyComOil, \
    ReplyComBooks, ReplyReplyComBooks
from django.db.models import Q, Count
from itertools import chain
from .form import UserRegForm, UserAuthForm, CommBookForm, ClientForm, CommOilForm, CountForm, OrderComForm
from .tasks import send_spam_email, send_6code


def CreateAvatar(model, name):
    try:
        image, _ = urlretrieve(f'http://localhost:8080/monster/{name}')
    except urllib.error.URLError:
        image = False
    if image:
        model.clientPhoto = File(open(image, 'rb'), name=f'{name}.img')
        model.save()


def createOrder(form, cart):
    steps = Step.objects.all().order_by('id')
    for step in steps:
        if step.id == 1:
            Buy_step.objects.create(
                buystepBuy=form,
                buystepStep=step,
                buystepDatestart=datetime.now(timezone.utc),
            )
        else:
            Buy_step.objects.create(
                buystepBuy=form,
                buystepStep=step,
            )
    for item in cart:
        if item['value'] != '-1':
            Buy_product.objects.create(
                buyproductBuy=form,
                buyproductProduct=item['product'].motoroilsvolums.prod,
                buyproductCount=int(item['count']),
                buyproductValue=item['value'],
            )
        else:
            Buy_product.objects.create(
                buyproductBuy=form,
                buyproductProduct=item['product'].prod,
                buyproductCount=int(item['count']),
                buyproductValue=item['value'],
            )


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
                self.cart[str(product) + ' ' + value] = {'value': value, 'count': count,
                                                         'price': price.motoroilsvolumsPrice}
        else:
            price = Books.objects.get(pk=product)
            if price.booksPrice:
                self.cart[str(product) + ' ' + value] = {'value': value, 'count': count,
                                                         'price': price.booksPrice}

    def delete(self, product, value):
        del self.cart[str(product) + ' ' + value]
        self.save()

    def clear(self):
        del self.sesson['cart']
        self.sesson.modified = True

    def get_total_price(self):
        return str(round(sum([i['price'] * int(i['count']) for i in self.cart.values()]), 2))

    def save(self):
        self.sesson['cart'] = self.cart
        self.sesson.modified = True

    def __len__(self):
        return sum([int(item['count']) for item in self.cart.values()])

    def __iter__(self):
        for prod in self.cart.keys():
            print(prod, 22222222222222222222222)
            self.cart[prod]['summa'] = str(round(self.cart[prod]['price'] * int(self.cart[prod]['count']), 2))
            if prod.split(' ')[-1] != '-1':
                self.cart[prod]['product'] = Motoroils.objects.get(pk=prod.split(' ')[0]).oilvolume.get(
                    motoroilsvolumsVolums=prod.split(' ')[1])
                print(self.cart[prod]['product'])
                yield self.cart[prod]
            else:
                self.cart[prod]['product'] = Books.objects.get(pk=prod.split(' ')[0])
                yield self.cart[prod]


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
                filter['trueoil'] = True
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
        print(request.POST)
        if 'like' in request.POST.keys():
            product = get_object_or_404(Motoroils,pk=pr)
            if not product.motoroilslikes.filter(pk=request.user.pk):
                product.motoroilslikes.add(User.objects.get(pk=request.user.pk))
                product.save()
        elif 'dislike' in request.POST.keys():
            product = get_object_or_404(Motoroils, pk=pr)
            if product.motoroilslikes.filter(pk=request.user.pk):
                print(123)
                product.motoroilslikes.remove(User.objects.get(pk=request.user.pk))
                product.save()
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
    likes = {
        'count': Motoroils.objects.get(pk=213).motoroilslikes.count(),
        'like': True if Motoroils.objects.get(pk=213).motoroilslikes.filter(pk=request.user.pk) else False,
    }
    param = {
        'cats': cats,
        'oil': oil,
        'form': form,
        'formadd': formadd,
        'comments': get_page,
        'cart': cart,
        'likes': likes,
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


def removecomment(request, genr, boo, comm, name):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            prod = get_object_or_404(Product, pk=boo)

            if 'books' == prod.product.categoryName:
                comment = Books.objects.get(pk=boo).comment.get(pk=comm)
            else:
                comment = Motoroils.objects.get(pk=boo).commentOil.get(pk=comm)
            comment.delete()
            messages.success(request, 'Comment has been removed')
        except (Commentsbook.DoesNotExist, Books.DoesNotExist, Commentsoil.DoesNotExist, Motoroils.DoesNotExist):
            messages.warning(request, "Can't delete comment")
        return redirect(f'/category/{name}/{genr}/{boo}')


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
            user.checkemail
        except User.checkemail.RelatedObjectDoesNotExist:
            CheckEmail.objects.create(
                client=user
            )
        except User.client.RelatedObjectDoesNotExist:
            clien = Client.objects.create(
                clientUser=user,
                slug=user.username,
            )
            CreateAvatar(clien, name)
            CheckEmail.objects.create(
                client=user
            )
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
                print(request.POST)
                if request.POST.get('clientEmail'):
                    status = user.checkemail
                    status.status = False
                    status.save()
                if cform.clientEmail:
                    user.email = cform.clientEmail
                    user.save()
        cform = ClientForm(instance=clien)
        res = []
        for i in clien.buy.filter(buystep__buystepDatefinish__isnull=True).distinct():
            x = {'status': i.buystep.get(
                Q(buystepDatestart__isnull=False) & Q(buystepDatefinish__isnull=True)).buystepStep.stepName
                , 'product': []}
            for i1 in i.buyproduct.all():
                if i1.buyproductValue == '-1':
                    x['product'].append(i1.buyproductProduct.books.booksTitle)
                else:
                    x['product'].append(i1.buyproductProduct.motoroils.motoroilsTitle)
            res.append(x)
        print(res)
        param = {
            'cats': cats,
            'client': clien,
            'cform': cform,
            'cart': cart,
            'order': res,
        }

    return render(request, 'profile.html', param)


def test(request):
    return HttpResponse('OK')


def oiladd(request, pk, pr):
    cart = Cart(request)
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
    cart = Cart(request)
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


def buy(request):
    cart = Cart(request)
    if request.method == "POST" and request.user.is_authenticated:
        form = OrderComForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.buyClient_id = request.user.pk
            form.save()
            createOrder(form, cart)
            cart.clear()
            send_spam_email.delay(request.user.email)
            messages.success(request, 'Order completed. You can see your status on your profile.')
            return redirect('/')
    cats = Category.objects.all()
    form = OrderComForm()
    user = User.objects.get(pk=request.user.pk).client
    if user.clientName and user.clientCountry and user.clientAddress and user.clientSecondname:
        check = True
    else:
        check = False
    param = {
        'form': form,
        'cats': cats,
        'check': check,
        'user': user,
        'carts': cart,
    }
    return render(request, 'buy.html', param)


def buyitem(request):
    if request.method == "GET" and request.user.is_authenticated:
        cart = Cart(request)
        if request.GET:
            cart.add(product=request.GET['pr'], value=request.GET['value'])
            cart.save()
    return redirect('/cart/buy/')


def myclear(request):
    Cart(request).clear()

    return HttpResponse('clear')


def logoutuser(request):
    logout(request)
    return redirect('/')


def checkemail(request):
    if request.user.is_authenticated and User.objects.get(pk=request.user.pk).checkemail:
        if request.method == "POST":
            try:
                code = int(request.POST['code'])
            except ValueError:
                messages.warning(request, 'Only numbers required')
                return render(request, 'checkemail.html', {})
            user = User.objects.get(pk=request.user.pk).checkemail
            dtime = (datetime.now(timezone.utc) + timedelta(seconds=10800)) - user.datetime
            if code == user.password and 120 > dtime.seconds:
                user.password = None
                user.status = True
                user.datetime = None
                user.save()
                messages.success(request, 'You have verified your email')
                return redirect(f'/profile/{request.user.username}')
            return render(request, 'checkemail.html', {})
        send_6code.delay(request.user.username)
        return render(request, 'checkemail.html', {})


def reply(request, category, pk, pkcom):
    if request.user.is_authenticated and request.method == 'POST':
        if category == 'oils' and request.POST.get('text'):
            com = Commentsoil.objects.get(pk=pkcom)
            ReplyComOil.objects.create(
                commentMain=com,
                replyUser_id=request.user.pk,
                text=request.POST.get('text'),
            )
            return redirect(f'/category/oils/{Motoroils.objects.get(pk=pk).motoroilsProducer.pk}/{pk}/')
        elif category == 'books' and request.POST.get('text'):
            com = Commentsbook.objects.get(pk=pkcom)
            ReplyComBooks.objects.create(
                commentMain=com,
                replyUser_id=request.user.pk,
                text=request.POST.get('text'),
            )
            return redirect(f'/category/books/{Books.objects.get(pk=pk).booksGenre.pk}/{pk}/')

def rreply(request, category, pk, pkcom,rpkcom):
    if request.user.is_authenticated and request.method == 'POST':
        if category == 'oils' and request.POST.get('text'):
            com = Commentsoil.objects.get(pk=pkcom).replyoil.get(pk=rpkcom)
            ReplyReplyComOil.objects.create(
                commentMain_id=rpkcom,
                replyUser_id=request.user.pk,
                text=request.POST.get('text'),
            )
            return redirect(f'/category/oils/{Motoroils.objects.get(pk=pk).motoroilsProducer.pk}/{pk}/')
        elif category == 'books' and request.POST.get('text'):
            print(category, pk, pkcom, rpkcom)
            com = ReplyComBooks.objects.get(pk=rpkcom)
            print(request.POST)
            ReplyReplyComBooks.objects.create(
                commentMain=com,
                replyUser_id=request.user.pk,
                text=request.POST.get('text'),
            )
            return redirect(f'/category/books/{Books.objects.get(pk=pk).booksGenre.pk}/{pk}/')

def removereply(request, category, pk, pkcom):
    if request.user.is_authenticated:
        if category == 'oils':
            reply = get_object_or_404(ReplyComOil, pk=pkcom)
            if reply.replyUser.pk == request.user.pk or request.user.is_staff:
                reply.delete()
                messages.success(request, 'Comment has been removed')
                return redirect(f'/category/oils/{Motoroils.objects.get(pk=pk).motoroilsProducer.pk}/{pk}/')
        elif category == 'books':
            reply = get_object_or_404(ReplyComBooks, pk=pkcom)
            if reply.replyUser.pk == request.user.pk or request.user.is_staff:
                reply.delete()
                messages.success(request, 'Comment has been removed')
                return redirect(f'/category/books/{Books.objects.get(pk=pk).booksGenre.pk}/{pk}/')

def removerreply(request, category, pk, rrpkcom):
    if request.user.is_authenticated:
        if category == 'oils':
            rreply = get_object_or_404(ReplyReplyComOil, pk=rrpkcom)
            if  rreply.replyUser.pk == request.user.pk or request.user.is_staff:
                rreply.delete()
                messages.success(request, 'Comment has been removed')
                return redirect(f'/category/oils/{Motoroils.objects.get(pk=pk).motoroilsProducer.pk}/{pk}/')
        elif category == 'books':
            rreply = get_object_or_404(ReplyReplyComBooks, pk=rrpkcom)
            if rreply.replyUser.pk == request.user.pk or request.user.is_staff:
                rreply.delete()
                messages.success(request, 'Comment has been removed')
                return redirect(f'/category/books/{Books.objects.get(pk=pk).booksGenre.pk}/{pk}/')



# class SortComment:
#     def __init__(self, pk, category):
#         if category == 'books':
#             self.product = Books.objects.filter(pk=pk)
#         else:
#             self.product = Motoroils.objects.filter(pk=pk)
#         if self.product:
#             self.product = self.product[0]
#         self.category = category
#     def __len__(self):
#         return len(self.product)
#
#     def __iter__(self):
#         if self.category == 'oils':
#             for comment in self.product.commentOil:
#
#
#     def time_before(self, time):
#         time = datetime.now(timezone.utc) - time
#         if time.days:
#             return str(time.days) + ' days ago'
#         elif time.seconds // 3600:
#             return str(time.seconds // 3600 + 1) + ' hours ago'
#         else:
#             return str(time.seconds // 60) + ' minutes ago'
