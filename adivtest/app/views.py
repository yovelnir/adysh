import pyrebase
from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib.auth import login, logout , authenticate 
from django.contrib.auth.models import User
from django.db import IntegrityError 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse 
from django.contrib import messages



def login_user(request): 
    if request.method == 'GET': 
        return render (request, 'index.html', {'form':AuthenticationForm()}) 
    else: 
        user = authenticate(request, username= request.POST['uid'], password= request.POST['upassword']) 
        #some weird stuff with authenticate function
        if user is None: 
            context = messages.error(request,'username or password not correct')        
            return render (request, 'index.html', context) 
        else:
            login(request, user)
            if user.is_superuser:  
                response = redirect('/admin/')
                return response
            else: 
                response = redirect('/main_ASM/')
                return response  #will be needed for each type of persona 


@login_required
def logout_user(request): 
    logout(request) 
    return render(request, 'index.html')

@login_required
def main_ASM(request): 
    return render(request, 'main_ASM.html')