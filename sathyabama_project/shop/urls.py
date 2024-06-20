from django.urls import path
from . import views
 
urlpatterns= [
    path('',views.home,name="home"),
   
    path('register',views.register,name="register"),
    path('login',views.login_page,name="login"),
    path('logout',views.logout_page,name="logout"),
    path('cart',views.viewcart,name="cart"),
    path('fav',views.fav_page,name="fav"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('remove_fav/<str:fid>',views.remove_fav,name="remove_fav"),
    path('remove_cart/<str:cid>',views.remove_cart,name="remove_cart"),
    path('collections',views.collections,name="collections"),
    path('collections/<str:name>',views.collectionsview,name="collections"),
    path('collections/<str:cname>/<str:pname>',views.product_details,name="product_details"),
    path('addtocart',views.add_to_cart,name="addtocart"),

    path('checkout',views.index,name="checkout"),
    path('place-order',views.placeorder,name="placeorder"),

    path('proceed-to-pay',views.razorpaycheck),
    path('my-orders',views.index1,name="myorders"),
    path('view-order/<str:t_no>',views.vieworder,name="orderview"),

    path('product-list',views.productlistAjax),
    path('searchproduct',views.searchproduct, name='searchproduct'),

    path('forget-password/' , views.ForgetPassword , name="forget_password"),
    path('change-password/<token>/' , views.ChangePassword , name="change_password"),

]