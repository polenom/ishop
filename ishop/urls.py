from django.contrib import admin
from django.urls import path, include
from .views import test, startpage, pagecategory, loginPage, registerPage, pagegenre, book

urlpatterns = [
    path('', startpage),
    path('category/<slug:category>/', pagecategory, name='category'),
    path('category/books/<int:pk>/',pagegenre, name='booksgenre' ),
    path('login/', loginPage, name='login'),
    path('register/', registerPage, name='register'),
    path('category/books/<int:genr>/<int:boo>', book, name='book')
]

