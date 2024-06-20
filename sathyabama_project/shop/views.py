from contextlib import ContextDecorator
from pipes import Template
from django.http import  JsonResponse
from django.shortcuts import redirect, render
from shop.form import CustomUserForm
from django.contrib.auth.decorators import login_required
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import json
import random
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .helpers import send_forget_password_mail
 
 
def home(request):
  products=Product.objects.filter(trending=1)
  return render(request,"shop/index.html",{"products":products})
 
def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"shop/fav.html",{"fav":fav})
  else:
    return redirect("/")
 
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")
 
 
 
 
def viewcart(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"shop/cart.html",{"cart":cart})
  else:
    return redirect("/")
 
def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")
 
 
 
def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
 
 
def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
 
def logout_page(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request,"Logged out Successfully")
  return redirect("/")
 
 
def login_page(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
      name=request.POST.get('username')
      pwd=request.POST.get('password')
      user=authenticate(request,username=name,password=pwd)
      if user is not None:
        login(request,user)
        messages.success(request,"Logged in Successfully")
        return redirect("/")
      else:
        messages.error(request,"Invalid User Name or Password")
        return redirect("/login")
    return render(request,"shop/login.html")
 
def register(request):
  form=CustomUserForm()
  if request.method=='POST':
    form=CustomUserForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request,"Registration Success You can Login Now..!")
      return redirect('/login')
    else:
      messages.success(request,"Invalid details..!")
  return render(request,"shop/register.html",{'form':form})
 
 
def collections(request):
  catagory=Catagory.objects.filter(status=0)
  return render(request,"shop/collections.html",{"catagory":catagory})
 
def collectionsview(request,name):
  if(Catagory.objects.filter(name=name,status=0)):
      products=Product.objects.filter(category__name=name)
      return render(request,"shop/products/index2.html",{"products":products,"category_name":name})
  else:
    messages.warning(request,"No Such Catagory Found")
    return redirect('collections')
 
 
def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
      if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()
        return render(request,"shop/products/product_details.html",{"products":products})
      else:
        messages.error(request,"No Such Produtct Found")
        return redirect('collections')
    else:
      messages.error(request,"No Such Catagory Found")
      return redirect('collections')


@login_required(login_url='login')
def index(request):
  rawcart=Cart.objects.filter(user=request.user)
  for item in rawcart:
    if item.product_qty > item.product.quantity:
      Cart.objects.delete(id=item.id)
  cartitems = Cart.objects.filter(user=request.user)
  total_price=0
  for item in cartitems:
         total_price=total_price + item.product.selling_price * item.product_qty


  userprofile=Profile.objects.filter(user=request.user).first() 

  context={'cartitems':cartitems,'total_price':total_price,'userprofile':userprofile}
  return render(request,"shop/checkout.html",context)


def searchproduct(request):
  if request.method == 'POST':
    searchedterm=request.POST.get('productsearch')
    if searchedterm =="":
      return redirect(request.META.get('HTTP_REFERER'))
    else:
      product= Product.objects.filter(name__contains=searchedterm).first()
      if product:
        return redirect('collections/'+product.category.name+'/'+product.name)
      else:
        messages.info(request,"No product matched your search")
        return redirect(request.META.get('HTTP_REFERER')) 
  return redirect(request.META.get('HTTP_REFERER')) 




@login_required(login_url='login')
@csrf_exempt
def placeorder(request):
  if request.method == 'POST':

    currentuser = User.objects.filter(id=request.user.id).first()

    if not currentuser.first_name :
      currentuser.first_name=request.POST.get('fname')
      currentuser.last_name=request.POST.get('lname')
      currentuser.save()


    if not Profile.objects.filter(user=request.user):
       userprofile=Profile()
       userprofile.user=request.user
       userprofile.phone = request.POST.get('phone')
       userprofile.address = request.POST.get('address')
       userprofile.city = request.POST.get('city')
       userprofile.state = request.POST.get('state')
       userprofile.country = request.POST.get('country')
       userprofile.pincode = request.POST.get('pincode')
       userprofile.save()

    neworder = Order()
    neworder.user = request.user
    neworder.fname = request.POST.get('fname')
    neworder.lname = request.POST.get('lname')
    neworder.email = request.POST.get('email')
    neworder.phone = request.POST.get('phone')
    neworder.address = request.POST.get('address')
    neworder.city = request.POST.get('city')
    neworder.state = request.POST.get('state')
    neworder.country = request.POST.get('country')
    neworder.pincode = request.POST.get('pincode')

    neworder.payment_mode = request.POST.get('payment_mode')
    neworder.payment_id = request.POST.get('payment_id')

    cart = Cart.objects.filter(user=request.user)
    cart_total_price = 0
    for item in cart:
      cart_total_price = cart_total_price + item.product.selling_price * item.product_qty

    neworder.total_price = cart_total_price
    trackno ='jwhl'+str(random.randint(1111111,5555555))
    while Order.objects.filter(tracking_no=trackno) is None:
      trackno ='jwhl'+str(random.randint(1111111,5555555))
    neworder.tracking_no = trackno
    neworder.save()

    neworderitems = Cart.objects.filter(user=request.user)
    for item in neworderitems:
      OrderItem.objects.create(
          order=neworder,
          product=item.product,
          price=item.product.selling_price,
          quantity=item.product_qty )

      # to decrease the product quantity from available stock
      orderproduct = Product.objects.filter(id=item.product_id).first()
      orderproduct.quantity = orderproduct.quantity -item.product_qty
      orderproduct.save()

    # to clear usrs cart 
    Cart.objects.filter(user=request.user).delete()
    messages.success(request,'Your order has been placed successfully')
    
    

    payMode = request.POST.get('payment_mode')
    if (payMode == "Razorpay"):
      return JsonResponse({'status':'Your order has been placed successfully'})
    else:
      return JsonResponse({'status':'Your order has been placed successfully'})


      
  return redirect('/')



@login_required(login_url='login')
def razorpaycheck(request):
  cart=Cart.objects.filter(user=request.user)
  total_price=0
  for item in cart:
    total_price= total_price + item.product.selling_price * item.product_qty

  return JsonResponse({
    'total_price':total_price
    })


# def orders(request):
#   return render(request,'shop/search.html')


def index1(request):
  orders = Order.objects.filter(user=request.user)
  context={'orders':orders}
  return render(request,'shop/orders.html',context)



@login_required(login_url='login')
def vieworder(request, t_no):
  order = Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
  orderitems = OrderItem.objects.filter(order=order)
  context = {'order':order,'orderitems':orderitems}
  return render(request,'shop/view.html',context)


def productlistAjax(request):
  products=Product.objects.filter(status=0).values_list('name',flat=True)
  productsList=list(products)

  return JsonResponse(productsList, safe=False)







def ChangePassword(request , token):
    context = {}
    
    
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        context = {'user_id' : profile_obj.user.id}
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'No user id found.')
                return redirect(f'/change-password/{token}/')
                
            
            if  new_password != confirm_password:
                messages.success(request, 'both should  be equal.')
                return redirect(f'/change-password/{token}/')
                         
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/login/')
            
            
            
        
        
    except Exception as e:
        print(e)
    return render(request , 'change-password.html' , context)


import uuid
def ForgetPassword(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            
            if not User.objects.filter(username=username).first():
                messages.success(request, 'Not user found with this username.')
                return redirect('/forget-password/')
            
            user_obj = User.objects.get(username = username)
            token = str(uuid.uuid4())
            profile_obj= Profile.objects.get(user = user_obj)
            profile_obj.forget_password_token = token
            profile_obj.save()
            send_forget_password_mail(user_obj.email , token)
            messages.success(request, 'An email is sent.')
            return redirect('/forget-password/')
                
    
    
    except Exception as e:
        print(e)
    return render(request , 'forget-password.html')