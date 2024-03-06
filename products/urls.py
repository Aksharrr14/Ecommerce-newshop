from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .views import register_user

#leave as empty string for base url
urlpatterns=[
    path('',views.store,name="store"),
    path('cart/', views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('update_item/',views.updateItem,name="update_item"),
    path('process_order/',views.processOrder,name="update_item"),
    #path('login/',LoginView.as_view(template_name='login.html',success_url=reverse_lazy('store')),name="login"),
    #path('logout/',LogoutView.as_view(),name='logout'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('register/',views.register_user,name='register')
]   