from django.contrib import admin
from django.urls import path, include
from .views import test, startpage, pagecategory, loginPage, registerPage, pagegenre, book, removecomment, profile, pageoilproducer, oil

urlpatterns = [
    path('', startpage),
    path('category/<slug:category>/', pagecategory, name='category'),
    path('category/books/<int:pk>/', pagegenre, name='booksgenre'),
    path('login/', loginPage, name='login'),
    path('register/', registerPage, name='register'),
    path('category/books/<int:genr>/<int:boo>', book, name='book'),
    path('category/books/<int:genr>/<int:boo>/<int:comm>/remove/', removecomment, name='removecomment'),
    path('profile/<slug:name>', profile, name='profile'),
    path('category/oils/<int:pk>/', pageoilproducer, name='oilproducer'),
    path('category/oils/<int:pk>/<int:pr>', oil, name='oil'),
]
