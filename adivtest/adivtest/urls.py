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
    path('home/', views.postLogin, name = 'home'),
    path('main_Student/', views.main_Student, name = 'main_Student'),       #path for Student user 
    path('main_ASM/',views.main_ASM,name='main_ASM'),         #path to main page for ASM   
    path('create_user/',views.create_user, name='create_user'),
    path('inventory_stock_ASM/',views.inventory_stock, name='inventory_stock_ASM'), 
    path('inventory_stock_Manager/',views.inventory_stock, name='inventory_stock_Manager'),
    path('delete_user/',views.remove_user, name='delete_user'),
    path('logout/', views.logout, name='logout'),
    path('submit_an_order_ASM/',views.submit_an_order_ASM,name='submit_an_order_ASM'),
    path('send_requirements/',views.send_requirements, name='send_requirements'),
    path('remove_from_course/', views.remove_from_course, name='remove_from_course'),
    path('logout/', views.logout, name='logout'), 
    path('student_courses/', views.student_courses, name='student_courses'),
    path('ordering_existing_items_ASM/',views.ordering_existing_items_table,name='ordering_existing_items'),
    path('ordering_existing_items_request/',views.ordering_existing_items_request,name='ordering_existing_items_request'),
    path('student_ordering/', views.student_ordering, name="student_ordering"),
    path('ordering_existing_items_ASM/',views.order_status,name='ordering_existing_items'),
    path('order_status/',views.order_status,name='order_status'),
    path('ordering_new_items/',views.ordering_new_items,name='ordering_new_items'),
    path('pickup/', views.pickup, name = 'pickup'),
    path('pickup_schedule/', views.pickup_schedule, name='pickup_schedule'),
    path('manage_orders/',views.manage_orders,name='manage_orders'),
     path('manage_orders_approve/',views.manage_orders_approve,name='manage_orders_approve'),

]