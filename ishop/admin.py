from datetime import datetime

from django.contrib import admin
from .models import City, Client, Buy, Step, Buy_step, Category, Product, Buy_product, Author, Genre, Books, \
    Oilproducer, Motoroils, Motoroilsvolums


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
    list_display = ('buyClient', 'buyDescription')
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


admin.site.register(City)
admin.site.register(Client)
admin.site.register(Buy, Buy_admin)
admin.site.register(Step)
admin.site.register(Buy_step, Buy_step_admin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Buy_product)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Books)
admin.site.register(Oilproducer)
admin.site.register(Motoroils)
admin.site.register(Motoroilsvolums)

# Register your models here.
