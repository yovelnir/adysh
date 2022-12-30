"""adivtest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from app import views # for rendering pages from html 
from django.conf import settings # for ?
from django.conf.urls.static import static #for css and pictures files to be included

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_page, name = 'login'),            #login page path
    path('home/', views.postLogin),
    path('main_Student/', views.main_Student, name = 'main_Student'),       #path for Student user 
    path('main_ASM/',views.main_ASM,name='main_ASM'),         #path to main page for ASM   
    path('create_user/',views.create_user, name='create_user'),
    path('inventory_stock_ASM/',views.inventory_stock, name='inventory_stock_ASM'), 
    path('inventory_stock_Manager/',views.inventory_stock, name='inventory_stock_Manager'),
    path('delete_user/',views.remove_user, name='delete_user'),
    path('logout/', views.logout, name='logout'), 
    path('student_courses/', views.student_courses, name='student_courses')
]