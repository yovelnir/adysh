import pyrebase
from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib.auth import login, logout , authenticate 
from django.contrib.auth.models import User
from django.db import IntegrityError 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages


config = {
    'apiKey': "AIzaSyAXmr_K0XssRKaC03Ad45bkRWt0Q43CI1w",
    'authDomain': "adysh-d6408.firebaseapp.com",
    'databaseURL': "https://adysh-d6408-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "adysh-d6408",
    'storageBucket': "adysh-d6408.appspot.com",
    'messagingSenderId': "449013193486",
    'appId': "1:449013193486:web:f3907584053a64ff28d55f"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

def postLogin(request):
    email = request.POST.get('email')
    pasw = request.POST.get('pass')
    try:
        user = authe.sign_in_with_email_and_password(email,pasw)
    except:
        message = "Invalid User! Please check email and password"
        return render(request,"login.html",{"message":message})
    session_id = user['idToken']
    request.session['uid']=str(session_id)
    request.session['email']=str(email)
    user_data = database.child('users').child(email[:email.index('@')]).get().val()

    if user_data['role'] == 1:
        return render(request,"main_Student.html",user_data)
    elif user_data['role'] == 2:
        return render(request,"main_Wmanager.html",user_data)
    elif user_data['role'] == 3:
        return render(request,"main_ASM.html",user_data)

def login_page(request):
    return render(request, 'login.html')

def logout(request):
    try:
        del request.session['uid']
    except:
        pass
    render(request, "login.html")
    return HttpResponseRedirect('/')

def main_Student(request): 
    return render(request, 'main_Student.html')

def main_ASM(request): 
    return render(request, 'main_ASM.html')

def create_user(request):
    full_name = "{} {}".format(request.POST.get('fname'),request.POST.get('lname'))
    num_id, role = int(request.POST.get('id')), int(request.POST.get('role'))
    email, password = request.POST.get('email'), request.POST.get('password')
    database.child('users').child(email[0:email.index('@')]).set({
        'full_name': full_name,
        'id': num_id,
        'role': role,
    })
    authe.create_user_with_email_and_password(email, password)
    email = request.session['email']
    user_data = database.child('users').child(email[:email.index('@')]).get().val()
    return render(request,"main_Wmanager.html", user_data)

def inventory_stock(request):
    inventory = database.child('Inventory').get()

    items=list()
    for i  in inventory.each():
        product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
        product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
        items.append((product_name,product_amount))

    return render(request, "inventory_stock.html", {'items':items})
