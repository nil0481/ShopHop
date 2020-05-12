from django.shortcuts import render
from django.http import HttpResponse
from . models import Product, Contact, Orders, OrderUpdate
from math import ceil
from django.views.decorators.csrf import csrf_exempt                # for csrf exempt when payment is made
from PayTm import Checksum
import json
# Create your views here.
MERCHANT_KEY = 'zT8E!v7XrRqu%XiZ';

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

def searchMatch(query,item):
    # return true only if query matches the item
    query=query.split(" ")[0]
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False
def search(request):
    # same as def index
    query = request.GET.get('search')
    allProds = []
    catprod = Product.objects.values('category', 'id')  # list of dictionaries [ {'category': 'home appliances', 'id': 13},...]
    # print(catprod)
    cats = {item['category'] for item in catprod}  # dictionary of {'Electrical', 'watch'....}
    # print (cats)
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)  # category wise List of products
        prod = [item for item in prodtemp if searchMatch(query, item)]
        # print(prod)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
        # print(allProds)
    params = {'allProds': allProds}
    if len(allProds) == 0 or len(query) < 2:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


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
                    response=json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json},default=str)             # items_json={"pr8":[2,"Usha Fan"]...}
                                                                                                                # for details in tracker
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    return render(request, 'shop/tracker.html')






def productView(request,myid):
    # getting products through their id

    product=Product.objects.filter(id=myid)
    # print(product)
    return render(request, 'shop/prodView.html', {'product': product[0]})   # As product is a list having 1 item only



def checkout(request):
    if request.method == "POST":
        items_json=request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')                    # '' is default value
        amount = request.POST.get('amount', '')                    # '' is default value
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address1', '') + "  " +  request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')

        order = Orders(items_json=items_json, name=name, email=email, phone=phone,
                       address=address, city=city, state=state, zip_code=zip_code, amount=amount)  # name(database)=name(variable here)
        order.save()
        update=OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank=True
        id=order.order_id
        # return render(request, 'shop/checkout.html',{'thank':thank, 'id':id})
        # request paytm for payment
        param_dict={
            'MID':'MlhzKX58583165425333',
            'ORDER_ID':str(order.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	    'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',             # payment successfull msg by paytm
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html',{'param_dict':param_dict})
    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    #  paytm will send post req
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            # print(response_dict['RESPCODE'])
        else:
            print('order was not successful because ' + response_dict['RESPMSG'])
            # print(response_dict['RESPCODE'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})




