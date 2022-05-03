from django.contrib import admin
from django.urls import path, include
from .views import test, startpage,pagecategory

urlpatterns = [
    path('', startpage),
    path('<slug:category>/', pagecategory)
]