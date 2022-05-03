from datetime import datetime

from django.contrib import admin
from django.contrib.admin import AdminSite, sites

from .models import City, Client, Buy, Step, Buy_step, Category, Product, Buy_product, Author, Genre, Books, \
    Oilproducer, Motoroils, Motoroilsvolums


class EventAdminSite(AdminSite):
    def get_app_list(self, request):
        ordering = {
            'Clients': 1,
            'Citys': 2,
            'Buys': 3,
            'Steps': 4,
            'Buy_steps': 5,
            'Buy_products': 6,
            'Categorys': 7,
            'Books': 8,
            'Authors': 9,
            'Genres': 10,
            'Motoroilss': 11,
            'Oilproducers': 12,
            'Motoroilsvolumss': 13

        }
        app_dict = super().get_app_list(request)
        app_dict[1]['models'].sort(key=lambda x: ordering[x['name']])
        return app_dict


mysite = EventAdminSite()
admin.site = mysite
sites.site = mysite


@admin.action(description='add_data_start')
def makedatenowstart(modeladmin, request, queryset):
    for query in queryset:
        if not query.buystepDatestart:
            query.buystepDatestart = datetime.now()
            query.save()
        #


@admin.action(description='add_data_finish')
def makedatenowfinish(modeladmin, request, queryset):
    for query in queryset:
        if not query.buystepDatefinish:
            query.buystepDatefinish = datetime.now()
            query.save()


class Buy_step_admin(admin.ModelAdmin):
    list_display = ('buystepBuy', 'buystepStep', 'buystepDatestart', 'buystepDatefinish')
    list_display_links = ('buystepBuy', 'buystepStep')
    search_fields = ('buystepBuy__id',)
    ordering = ('-buystepBuy', 'buystepStep__id')
    actions = [makedatenowstart, makedatenowfinish]
    date_hierarchy = 'buystepDatestart'


class Buy_admin(admin.ModelAdmin):
    list_display = ('id', 'buyClient', 'buyDescription')
    list_display_links = ('buyClient', 'buyDescription')
    search_fields = ('buyClient__clientUser__username',)
    ordering = ('-pk',)

    def save_model(self, request, obj, form, change):
        if change == False:
            for st in Step.objects.all():
                if st.pk == 1:
                    Buy_step.objects.create(buystepBuy=ord, buystepStep=st, buystepDatestart=datetime.now())
                else:
                    Buy_step.objects.create(buystepBuy=ord, buystepStep=st)
        else:
            super(Buy_admin, self).save_model(request, obj, form, change)


class Genre_admin(admin.ModelAdmin):
    list_display = ('id', 'genreName')
    search_fields = ('genreName',)


class Author_admin(admin.ModelAdmin):
    list_display = ('id', 'authorName')
    search_fields = ('authorName',)


class Category_admin(admin.ModelAdmin):
    list_display = ('id', 'categoryName')
    search_fields = ('categoryName',)


class Product_admin(admin.ModelAdmin):
    list_display = ('id', 'product')
    search_fields = ('product',)


class Books_admin(admin.ModelAdmin):
    list_display = ('booksProduct', 'booksTitle', 'booksDiscription', 'booksCount', 'booksPrice')
    list_display_links = ('booksProduct', 'booksTitle', 'booksDiscription', 'booksCount')
    exclude = ('booksProduct', 'booksSlug')
    list_filter = ('booksCount', 'booksPrice')

    def save_model(self, request, obj, form, change):
        if change == False:
            produd = Product.objects.create(product=Category.objects.get(categoryName='books'))
            new_book = form.save(commit=False)
            new_book.booksProduct = produd
            new_book.save()
        else:
            super(Books_admin, self).save_model(request, obj, form, change)


class Buy_product_admin(admin.ModelAdmin):
    list_display = ('title', 'buyproductBuy', 'buyproductCount')


class Client_admin(admin.ModelAdmin):
    list_display = ('clientUser', 'clientName', 'clientSecondname', 'clientCountry', 'clientBirthday')
    list_display_links = ('clientUser', 'clientName', 'clientSecondname', 'clientCountry', 'clientBirthday')
    search_fields = ('clientUser__username', 'clientName')
    ordering = ('-pk',)
    list_filter = ('clientCountry', 'clientBirthday')


class City_admin(admin.ModelAdmin):
    search_fields = ('cityName',)


class Oil_producer_admin(admin.ModelAdmin):
    search_fields = ('oilproducer',)

class Motor_oil_admin(admin.ModelAdmin):
    list_display = ('producer', 'motoroilsTitle', 'volums')
    list_display_links = ('producer', 'motoroilsTitle', )
    search_fields = ('motoroilsTitle',)

class Oil_volums_admin(admin.ModelAdmin):
    list_display = ('motoroilsvolums', 'motoroilsvolumsVolums', 'motoroilsvolumsPrice', 'motoroilsvolumsCount')
    list_display_links = ('motoroilsvolums', 'motoroilsvolumsVolums', 'motoroilsvolumsPrice', 'motoroilsvolumsCount')
    search_fields = ('motoroilsvolums', )




admin.site.register(City, City_admin)
admin.site.register(Client, Client_admin)
admin.site.register(Buy, Buy_admin)
admin.site.register(Step)
admin.site.register(Buy_step, Buy_step_admin)
admin.site.register(Category, Category_admin)

admin.site.register(Buy_product, Buy_product_admin)
admin.site.register(Author, Author_admin)
admin.site.register(Genre, Genre_admin)
admin.site.register(Books, Books_admin)
admin.site.register(Oilproducer, Oil_producer_admin)
admin.site.register(Motoroils, Motor_oil_admin)
admin.site.register(Motoroilsvolums, Oil_volums_admin)

# Register your models here.
