from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


def userPhotoPath(instance, filename):
    date = datetime.now()
    return f'static/Photo/{date.year}/{date.month}/{date.day}/username_{instance.userProfile}_id_{instance.userProfile.id}_{datetime.now()}.{filename.split(".")[1]}'


# Create your models here.
class City(models.Model):
    cityName = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.cityName


class Client(models.Model):
    clientUser = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='', related_name='client',
                                      primary_key=True)
    clientPhoto = models.FileField(upload_to=userPhotoPath, blank=True, default='', verbose_name='photo', null=True)
    clientName = models.CharField(max_length=30, blank=True, default='', verbose_name='first name', null=True)
    clientSecondname = models.CharField(max_length=30, blank=True, default='', verbose_name='second name', null=True)
    clientBirthday = models.DateTimeField(blank=True, null=True, verbose_name='birthday')
    clientCity = models.EmailField(max_length=200, verbose_name='email', null=True)
    clientCountry = models.ForeignKey(City, on_delete=models.SET_NULL, verbose_name='client', blank=True, null=True)
    clientAddress = models.CharField(max_length=200, default='', blank=True, null=True)
    slug = models.SlugField(null=True)

    def __str__(self):
        return self.clientUser.username


class Buy(models.Model):
    buyClient = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='buy', verbose_name='client')
    buyDescription = models.CharField(max_length=50, default='')

    def __str__(self):
        return str(self.id)


class Step(models.Model):
    stepName = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.stepName


class Buy_step(models.Model):
    buystepBuy = models.ForeignKey(Buy, models.CASCADE, verbose_name='number order')
    buystepStep = models.ForeignKey(Step, models.SET_NULL, null=True, verbose_name='step')
    buystepDatestart = models.DateTimeField(null=True, blank=True)
    buystepDatefinish = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.buystepStep)


class Category(models.Model):
    categoryName = models.CharField(max_length=30, unique=True)
    categorySlug = models.SlugField(null=True)

    def __str__(self):
        return self.categoryName

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categorys'

class Product(models.Model):
    product = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='product',
                                related_name='product')

    def __str__(self):
        return str(self.product)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class Buy_product(models.Model):
    buyproductBuy = models.ForeignKey(Buy, on_delete=models.CASCADE, verbose_name='buyproductBuy',
                                      related_name='buyproduct')
    buyproductProduct = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='buyproduct',
                                          related_name='buyproduct')
    buyproductCount = models.IntegerField(default=1)

    def __str__(self):
        return str(self.buyproductProduct)

    class Meta:
        verbose_name = 'Buy_product'
        verbose_name_plural = 'Buy_products'


class Author(models.Model):
    authorName = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.authorName

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'


class Genre(models.Model):
    genreName = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return  self.genreName

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'


class Books(models.Model):
    booksProduct = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='book', primary_key=True, editable=False)
    booksTitle = models.CharField(max_length=100)
    booksDiscription = models.CharField(max_length=300, default='')
    booksAuthor = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='books',
                                    verbose_name='author')
    booksGenre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, verbose_name='books')
    booksPrice = models.FloatField()
    booksCount = models.IntegerField()
    booksSlug = models.SlugField(unique=True, null=True,blank=True)



    def __str__(self):
        return self.booksTitle

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.booksSlug:
            self.booksSlug = slugify(self.booksTitle)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)


    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'


class Oilproducer(models.Model):
    oilproducer = models.CharField(max_length=50)


class Motoroils(models.Model):
    motoroilsProducer = models.ForeignKey(Oilproducer, on_delete=models.SET_NULL, null=True, related_name='oil')
    motoroilsTitle = models.CharField(max_length=200, default='')
    motoroilsSlug = models.SlugField(unique=True)


class Motoroilsvolums(models.Model):
    motoroilsvolums = models.ForeignKey(Motoroils, on_delete=models.CASCADE, related_name='oilvolume')
    motoroilsvolumsPrice = models.FloatField()
    motoroilsvolumsCount = models.IntegerField()
    motoroilsvolumsVolums = models.FloatField()
