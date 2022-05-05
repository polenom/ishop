from django.core.files import File
from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from ishop.models import Motoroils, Product, Oilproducer, Motoroilsvolums, Books, Author, Genre, Category
from urllib.request import urlretrieve

urlk1 = 'https://auto.1k.by/spares-motoroil/'
urlbb = 'https://biblio.by/biblio-books.html'


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--k1', '-k', action='append', type=int)
        parser.add_argument('--bb', '-b', action='append', type=int)

    def handle(self, *args, **options):
        if options.get('k1'):
            page = 1
            addInModelsProduct = 0
            countPosition = options.get('k1')[0]
            cacheOilProducer = []
            while addInModelsProduct < countPosition:
                listHtml = BeautifulSoup(requests.get(urlk1 + f'page{page}').text, 'html.parser')
                page += 1

                for oil in listHtml.findAll('div', 'prod__in'):
                    listName = oil.a.text.split()
                    oilname = listName[2] if listName[0] in ['Моторное', 'моторное', 'Масло', 'масло'] else listName[0]
                    oilVolum = listName[-1] if '(' not in listName[-1] else listName[-2]
                    oilnameProduct = ' '.join(listName[2:-1]) if listName[0] in ['Моторное', 'моторное', 'Масло',
                                                                                 'масло'] else ' '.join(listName[2:-1])
                    oildesc = oil.p.text
                    try:
                        oilPrice = oil.find('span', 'money__val').text
                    except AttributeError:
                        oilPrice = '0'

                    oilImage = oil.img['src']
                    if oilname not in cacheOilProducer:
                        try:
                            getOIlprod = Oilproducer.objects.get(oilproducer=oilname)
                        except Oilproducer.DoesNotExist:
                            getOILprod = Oilproducer.objects.create(oilproducer=oilname)
                    try:
                        getOIL = Motoroils.objects.get(motoroilsTitle=oilnameProduct)
                    except Motoroils.DoesNotExist:

                        getOIlprod = Oilproducer.objects.get(oilproducer=oilname)
                        name, _ = urlretrieve(oilImage)
                        getOIL = Motoroils.objects.create(
                            prod=Product.objects.create(product=Category.objects.get(categoryName='oils')),
                            motoroilsProducer=getOIlprod,
                            motoroilsPhoto=File(open(name, 'rb'), name=oilImage.split('/')[-1]),
                            motoroilsTitle=oilnameProduct,
                            motoroilsDescription=oildesc,
                            motoroilsSlug=oilnameProduct.replace(' ', ''),
                        )
                    if not getOIL.oilvolume.filter(motoroilsvolumsVolums=float(oilVolum[:-1])):
                        Motoroilsvolums.objects.create(
                            motoroilsvolums=getOIL,
                            motoroilsvolumsVolums=float(oilVolum[:-1]),
                            motoroilsvolumsPrice=float(oilPrice.replace(',', '.').split()[0]),
                            motoroilsvolumsCount=10
                        )

                    addInModelsProduct += 1
                    print('k', addInModelsProduct)
                    if addInModelsProduct >= countPosition:
                        break
        if options.get('bb'):
            page = 1
            addInModelsProduct = 0
            countPosition = options.get('bb')[0]
            params = {
                'p': page,
            }
            while addInModelsProduct < countPosition:
                booksSite = BeautifulSoup(requests.get(urlbb, params=params).text, 'html.parser')
                for bookSite in booksSite.findAll('div', 'span13'):
                    urlbook = bookSite.a['href']
                    bookParser = BeautifulSoup(requests.get(urlbook).text, 'html.parser')
                    bookAuthor = bookSite.p.text
                    bookGenre = bookParser.find('div', 'breadcrumbs').findAll('li')[-2].a.text
                    bookDisc = bookParser.find('div', 'std').text
                    bookTitle = bookSite.a['title']
                    bookCount = 10
                    bookPrice = bookSite.find('span', 'price').text
                    bookImage = bookSite.img['src']
                    try:
                        bookAuthor = Author.objects.get(authorName=bookAuthor)
                    except Author.DoesNotExist:
                        bookAuthor = Author.objects.create(authorName=bookAuthor)
                    try:
                        booksGenre = Genre.objects.get(genreName=bookGenre)
                    except Genre.DoesNotExist:
                        booksGenre = Genre.objects.create(genreName=bookGenre)


                    if not Books.objects.filter(booksTitle=bookTitle):
                        name, _ = urlretrieve(bookImage)
                        newBook = Books.objects.create(
                            prod=Product.objects.create(product=Category.objects.get(categoryName='books')),
                            booksPhoto = File(open(name,'rb'), name=bookImage.split('/')[-1]),
                            booksTitle=bookTitle[:100],
                            booksDiscription=bookDisc[:1700],
                            booksAuthor=bookAuthor,
                            booksGenre=booksGenre,
                            booksPrice=float(bookPrice.replace(',','.').split()[0]),
                            booksCount=bookCount,
                            # booksSlug=bookTitle.replace(' ',''),
                        )

                    print(addInModelsProduct)
                    addInModelsProduct += 1
                    if addInModelsProduct >= countPosition:
                        break
                params['p']+=1

        # print(options['count'],777777777777777777777)
        # print(options['k1'],1)
