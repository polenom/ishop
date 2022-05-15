from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from ishop.models import Commentsbook, Client


class UserRegForm(UserCreationForm):
    username = forms.CharField(label='Username', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'username', 'required': 'True'}))
    email = forms.CharField(label='Email', required=False, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'id': 'floatingEmail', 'placeholder': 'Email', 'required': 'True'}))
    password1 = forms.CharField(label='Password', required=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'floatingPassword', 'placeholder': 'password', 'required': 'True'}))
    password2 = forms.CharField(label='Confim password', required=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'floatingPassword', 'placeholder': 'password', 'required': 'True'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserAuthForm(AuthenticationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'floatingPassword', 'placeholder': 'password'}))


class CommBookForm(forms.ModelForm):
    class Meta:
        model = Commentsbook
        fields = ('combookText',)


class ClientForm(forms.ModelForm):
    clientPhoto = forms.ImageField(label='Photo', required=False)
    clientBirthday = forms.DateField(label='Birthday', required=False,
                                     widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},
                                                            format=('%Y-%m-%d')))
    clientSecondname = forms.CharField(label='surname', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'surname', 'class': 'form-control'}))
    clientPhoto = forms.FileField(label='Photo', required=False,
                                  widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Photo'}))
    clientMobile = forms.CharField(label='Mobile', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mobile'}))
    clientEmail = forms.EmailField(label='Email',required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    clientAddress = forms.CharField(label='Mobile',required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'address'}))
    clientName = forms.CharField(label='Name',required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name'}))

    class Meta:
        model = Client
        fields = ('clientPhoto', 'clientName', 'clientSecondname', 'clientBirthday', 'clientEmail', 'clientCountry',
                  'clientAddress', 'clientMobile')
