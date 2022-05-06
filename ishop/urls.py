from django.contrib import admin
from django.urls import path, include
from .views import test, startpage, pagecategory, loginPage, registerPage

urlpatterns = [
    path('', startpage),
    path('category/<slug:category>/', pagecategory),
    path('login/', loginPage, name='login'),
    path('register/', registerPage, name='register')
]
