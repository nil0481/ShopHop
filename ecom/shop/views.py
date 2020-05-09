from django.shortcuts import render
from django.http import HttpResponse
from . models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
# Create your views here.

def index(request):
    # products=Product.objects.all()

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
    if request.method=="POST":

        name=request.POST.get('name','')            # '' is default value
        email=request.POST.get('email','')
        phone=request.POST.get('phone','')
        desc=request.POST.get('desc','')
        # print(name,email)

        contact = Contact(name=name, email=email, phone=phone, desc=desc)       # name(database)=name(variable here)
        contact.save()
    return render(request, 'shop/contact.html')



def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')                     # '' is default value
        email = request.POST.get('email', '')

        try:
            order= Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update=OrderUpdate.objects.filter(order_id=orderId)
                updates=[]
                for item in update:
                    updates.append({'text':item.update_desc, 'time':item.timestamp})
                    response=json.dumps([updates, order[0].items_json],default=str)             # items_json={"pr8":[2,"Usha Fan"]...}
                                                                                                                # for details in tracker
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request, 'shop/tracker.html')



def search(request):
    return render(request, 'shop/search.html')



def productView(request,myid):
    # getting products through their id

    product=Product.objects.filter(id=myid)
    # print(product)
    return render(request, 'shop/prodView.html', {'product': product[0]})   # As product is a list having 1 item only



def checkout(request):
    if request.method == "POST":
        items_json=request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')                     # '' is default value
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address1', '') + "  " +  request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')

        order = Orders(items_json=items_json, name=name, email=email, phone=phone, address=address, city=city, state=state, zip_code=zip_code)  # name(database)=name(variable here)
        order.save()
        update=OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank=True
        id=order.order_id
        return render(request, 'shop/checkout.html',{'thank':thank, 'id':id})

    return render(request, 'shop/checkout.html')




