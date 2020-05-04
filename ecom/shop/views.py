from django.shortcuts import render
from django.http import HttpResponse
from . models import Product
from math import ceil
# Create your views here.

def index(request):
    # products=Product.objects.all()
    # print(products)
    # n=len(products)
    # # no of slides
    # nSlides = n//4 + ceil((n/4)-(n//4))

    #######commented as it will show every prod; we want categories####
    # params={'no_of_slides':nSlides, 'range':range(1,nSlides), 'product':products}
    # allProds=[[products,range(1,nSlides),nSlides], [products,range(1,nSlides),nSlides]]

    allProds=[]
    catprod=Product.objects.values('category','id')    #list of dictionaries [ {'category': 'home appliances', 'id': 13},...]
    # print(catprod)
    cats={item['category'] for item in catprod}         #dictionary of {'Electrical', 'watch'....}
    # print (cats)


    for cat in cats:
        prod=Product.objects.filter(category=cat)         #category wise List of products
        # print(prod)
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nSlides),nSlides])
        # print(allProds)

    params={'allProds':allProds}


    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

def tracker(request):
    return render(request, 'shop/tracker.html')

def search(request):
    return render(request, 'shop/search.html')

def productView(request,myid):
    # getting products through their id

    product=Product.objects.filter(id=myid)
    # print(product)
    return render(request, 'shop/prodView.html', {'product': product[0]})   # As product is a list having 1 item only

def checkout(request):
    return render(request, 'shop/checkout.html')







