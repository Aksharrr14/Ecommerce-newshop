from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserProfile(models.Model):
    user=models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    is_seller=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Seller' if self.is_seller else 'Buyer'}"

class Customer(models.Model):
    user_profile=models.OneToOneField(UserProfile, null=True, blank=True, on_delete=models.CASCADE)
    name=models.CharField(max_length=200, null=True)
    email=models.CharField(max_length=200)

    # USERNAME_FIELD = 'email'


    def __str__(self):
        return self.name
    
class Product(models.Model):
    name= models.CharField(max_length=200, null=True)
    price= models.FloatField()
    #digital=models.BooleanField(default=False)
    image=models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url

    
class Order(models.Model):
    customer=models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_ordered=models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(default=False)
    transaction_id=models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)
    
    @property
    def shipping(self): 
        shipping=True
        return shipping
    
    @property
    def get_cart_total(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.quantity for item in orderitems])
        return total
    
class OrderItem(models.Model):
    product= models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    order=models.ForeignKey(Order,null=True, blank=True, on_delete=models.SET_NULL)
    quantity= models.IntegerField(default=0,null=True,blank=True)
    date_added= models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total=self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer=models.ForeignKey(User, null=True,blank=True,on_delete=models.SET_NULL)
    order=models.ForeignKey(Order,null=True,blank=True,on_delete=models.SET_NULL)
    address=models.CharField(max_length=200, null=False)
    city=models.CharField(max_length=20,null=False)
    state=models.CharField(max_length=50,null=False)
    zipcode=models.CharField(max_length=50,null=False)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
    
class APIData(models.Model):
    title=models.CharField(max_length=210)
    price=models.FloatField()
    image=models.URLField()

    def __str__(self):
        return self.title