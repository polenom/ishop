import requests
from bs4 import BeautifulSoup


u = 'https://biblio.by/biblio-books.html'
params = {
    'p':4
}
res = BeautifulSoup(requests.get(u,params=params).text, 'html.parser')
for i in res.findAll('div','span13'):
    print(i)

