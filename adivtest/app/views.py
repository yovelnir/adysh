import pyrebase
from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib.auth import login, logout , authenticate 
from django.contrib.auth.models import User
from django.db import IntegrityError 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse 
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
        return render(request,"Login.html",{"message":message})
    
    session_id = user['idToken']
    request.session['uid']=str(session_id)
    user_data = {
        'role': database.child('users').child(email[0:email.index('@')]).child('role').get().val(),
        'ID': database.child('users').child(email[0:email.index('@')]).child('id').get().val(),
        'name': database.child('users').child(email[0:email.index('@')]).child('full_name').get().val(),
    }

    if user_data['role'] == 1:
        return render(request,"main_ASM.html",user_data)
    else:
        return render(request,"main_Wmanager.html",user_data)

def login(request):
    return render(request, 'login.html')


@login_required
def logout_user(request): 
    logout(request) 
    return render(request, 'index.html')

@login_required
def main_ASM(request): 
    return render(request, 'main_ASM.html')