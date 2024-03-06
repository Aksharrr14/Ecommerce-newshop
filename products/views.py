# Create your views here.
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from .models import *
import datetime
import requests
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import ProductSerializer
from django.core.files.base import ContentFile
import json
from django.core.files.base import ContentFile
from .models import Product
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms

# Create your views here.
# def index(request):
#     api_url='https://fakestoreapi.com/products'
#     response=requests.get(api_url)
#     products=response.json()
#     #products=Products.objects.all()   #this returns all the objects we have in our database  and storing it in a variable
    
#     return render(request, 'index.html',{'products':products})

# def login(request):
#     if request.method=='POST':
#         form=

def login_user(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,("You are logged in now"))
            return redirect('store')
        else:
            messages.success(request,("There was some error"))
            return redirect('login')
    return render(request,'login.html',{})

def logout_user(request):
    logout(request)
    messages.success(request,("You  have now been logged out"))
    return redirect('store')



def store(request):
    if request.user.is_authenticated:
        # customer=User.objects.get(user=request.user)
        customer=request.user
        print(customer)
        customer=User.objects.get(username=customer)
        print(type(customer))
        order, created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0 , 'get_cart_items':0}
        cartItems=order['get_cart_items']

    products=Product.objects.all()
    fake_store_products=fetch_fake_store_data()
    all_products=list(products)+ fake_store_products
    context={'items':items,'products':all_products, 'cartItems':cartItems}
    return render(request, 'store.html',context)

def register_user(request):
    form=SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            #login in user
            user=authenticate(username=username,password=password)
            login(request, user)
            messages.success(request,"You have been signed in")
            return redirect('store')
            # user = form.save(commit=False)  # Create user without saving to the database
            # user.save()

            # Create associated Customer instance
            # customer = User.objects.create(username=form.cleaned_data['username'], email=form.cleaned_data['email'])

            login(request, user)  # Automatically log in the user after signup
            return redirect('store')  # Redirect to your desired page after signup
        else:
            messages.success(request,"There was some error")
            return redirect('register')
    else:
        return render(request, 'signup.html', {'form': form})

def cart(request):
    if request.user.is_authenticated:
        customer=request.user
        order, created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0 , 'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']

    context={'items':items, 'order':order,'cartItems':cartItems}
    return render(request,'cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0 , 'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']

    context={'items':items, 'order':order,'cartItems':cartItems}
    return render(request,'checkout.html',context)

def new(request):
    return HttpResponse("new products") 


def fetch_fake_store_data():
    url = 'https://fakestoreapi.com/products'
    response = requests.get(url)

    if response.status_code == 200:
        api_data = response.json()

        # Iterate through API data and create Product instances
        for item in api_data:
            name = item.get('title', '')
            price = item.get('price', 0)
            image_url = item.get('image', '')

            #Checking if the product already exists(checking name)
            existing_product=Product.objects.filter(name=name).first()
            if existing_product:
                # If the product exists, update its information (e.g., price)
                existing_product.price = price
                existing_product.save()
            else:

                # Download the image
                image_content = requests.get(image_url).content

                # Create a Product instance
                product = Product.objects.create(
                    name=name,
                    price=price,
                )

                # Save the image to the Product instance
                product.image.save(f'{name}_image.jpg', ContentFile(image_content), save=True)

        return api_data
    else:
        # Handle error, log, or raise an exception
        return None

# class SyncProductsView(APIView):
#     def get_fake_store_data(self):  
    


def updateItem(request):
    data= json.loads(request.body)
    productId=data['productId']
    action=data['action']
    print('Action:', action)
    print('Product:',productId)

    customer=request.user
    product= Product.objects.get(id=productId)
    order, created=Order.objects.get_or_create(customer=customer, complete=False)
    orderItem,created=OrderItem.objects.get_or_create(order=order, product=product)

    if action =='add':
        orderItem.quantity=(orderItem.quantity + 1) 
    elif action =='remove':
        orderItem.quantity=(orderItem.quantity -1)

    orderItem.save()

    if orderItem.quantity <=0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data= json.loads(request.body)

    if request.user.is_authenticated:
        customer=request.user
        order, created=Order.objects.get_or_create(customer=customer, complete=False)
        total= float(data['form']['total'])
        order.transaction_id=transaction_id

        if total ==order.get_cart_total:
            order.complete=True
        order.save()

        if order.shipping ==True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )


    else:
        print('User is not logged in..')
    return JsonResponse('Payment Completed!',safe=False)