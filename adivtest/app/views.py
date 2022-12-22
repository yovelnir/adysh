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

    ser_data = database.child('users').get()
    #----Saving user session id----
    session_id = user['idToken']
    request.session['uid']=str(session_id)
    #----Saving user's email in the current session to access database in other pages
    request.session['email']=str(email)
    short_mail = email[:email.index('@')]

    #----Checking user's role----
    if short_mail in database.child('users').child('students').get().val():
        user_data = database.child('users').child('students').child(short_mail).get().val()
        request.session['role'] = 'students'
    elif short_mail in database.child('users').child('managers').get().val():
        user_data = database.child('users').child('managers').child(short_mail).get().val()
        request.session['role'] = 'managers'
    elif short_mail in database.child('users').child('staff').get().val():
        user_data = database.child('users').child('staff').child(short_mail).get().val()
        request.session['role'] = 'staff'

    #----Rendering home page based on user's role----
    if request.session['role'] == 'students':
        return render(request,"main_Student.html",user_data)
    elif request.session['role'] == 'managers':
        return render(request,"main_Wmanager.html",user_data)
    elif request.session['role'] == 'staff':
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
    #-----Getting current session user data-----#
    email = request.session['email']
    user_data = database.child('users').child(request.session['role']).child(email[:email.index('@')]).get().val()
    #-----Getting current session user data-----#

    full_name = "{} {}".format(request.POST.get('fname'),request.POST.get('lname'))
    num_id, role = int(request.POST.get('id')), int(request.POST.get('role'))
    email, password = request.POST.get('email'), request.POST.get('password')
    short_mail = email[:email.index('@')]

    if short_mail not in database.child('users').child('students').get().val() \
    and short_mail not in database.child('users').child('staff').get().val() \
    and short_mail not in database.child('users').child('managers').get().val():
        if role == 1:
            user = authe.create_user_with_email_and_password(email, password)
            database.child('users').child('students').child(short_mail).set({
                'idToken': user['idToken'],
                'full_name': full_name,
                'id': num_id,
            })
        elif role == 2:
            user = authe.create_user_with_email_and_password(email, password)
            database.child('users').child('managers').child(short_mail).set({
                'idToken': user['idToken'],
                'full_name': full_name,
                'id': num_id,
            })
        elif role == 3:
            user = authe.create_user_with_email_and_password(email, password)
            database.child('users').child('staff').child(short_mail).set({
                'idToken': user['idToken'],
                'full_name': full_name,
                'id': num_id,
            })
    else:
        user_data['msg'] = "User already exists!"
    
    return render(request,"main_Wmanager.html", user_data)

def remove_user(request):
    #-----Getting current session user data-----#
    email = request.session['email']
    user_data = database.child('users').child(request.session['role']).child(email[:email.index('@')]).get().val()
    #-----Getting current session user data-----#

    email = request.POST.get('email')
    if email != request.session['email']:
        short_mail = email[:email.index('@')]
        if short_mail in database.child('users').child('students').get().val():
            idToken = database.child('users').child('students').child(short_mail).child('idToken').get().val()
            role = 1
        elif short_mail in database.child('users').child('managers').get().val():
            idToken = database.child('users').child('managers').child(short_mail).child('idToken').get().val()
            role = 2
        elif short_mail in database.child('users').child('staff').get().val():
            idToken = database.child('users').child('staff').child(short_mail).child('idToken').get().val()
            role = 3
            
        if idToken:
            authe.delete_user_account(idToken)

            if role == 1:
                database.child('users').child('students').child(short_mail).remove()
            elif role == 2:
                database.child('users').child('managers').child(short_mail).remove()
            elif role == 3:
                database.child('users').child('staff').child(short_mail).remove()

        else:
            user_data['msg'] = "User does not exist."
    else:
        user_data['msg'] = "You cannot remove your self!"

    return render(request,"main_Wmanager.html", user_data)

    

def inventory_stock(request):
    inventory = database.child('Inventory').get()

    if 'InStock' in request.POST: 
        filter = request.POST['InStock'] 
    elif 'OutOfStock' in request.POST:
        filter = request.POST['OutOfStock']
    else: 
        filter = '0'
    items = list()
     
#========InStock   
    if filter == '1': 
        for i in inventory.each(): 
            if database.child('Inventory').child(i.key()).child('Quantity').get().val() is not None:
                if database.child('Inventory').child(i.key()).child('Quantity').get().val() > 0: 
                    product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                    product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
                    items.append((product_name,product_amount)) 

        return render(request, "inventory_stock_ASM.html", {'items':items})  
#========OutOfStock
    if filter == '2': 
        for i in inventory.each(): 
            if database.child('Inventory').child(i.key()).child('Quantity').get().val() is not None:
                if database.child('Inventory').child(i.key()).child('Quantity').get().val() == 0: 
                    product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                    product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
                    items.append((product_name,product_amount)) 

        return render(request, "inventory_stock_ASM.html", {'items':items})  
#========ShowAll Case
    else: 
        for i in inventory.each():
            product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
            product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
            items.append((product_name,product_amount)) 
            
        return render(request, "inventory_stock_ASM.html", {'items':items})
