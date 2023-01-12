import pyrebase
from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib.auth import login, logout , authenticate 
from django.contrib.auth.models import User
from django.db import IntegrityError 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
import os
import firebase_admin
from firebase_admin import credentials, storage
from datetime import timedelta, date, datetime
import datetime
from calendar import monthrange
from django.http import HttpResponseBadRequest


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
storage1 = firebase.storage()
current_dir = os.getcwd()
cred = credentials.Certificate(f'{current_dir}/adysh-d6408-firebase-adminsdk-sd2zj-393e99226b.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'adysh-d6408.appspot.com'
})


def postLogin(request):
    if request.session.get('uid'):
        email = request.session['email']
        short_mail = email[:email.index("@")]
    else:
        email = request.POST.get('email')
        pasw = request.POST.get('pass')
        
        try:
            user = authe.sign_in_with_email_and_password(email,pasw)
        except:
            message = "Invalid User! Please check email and password"
            return render(request,"login.html",{"message":message})

        #----Saving user session id----#
        session_id = user['idToken']
        request.session['uid']=str(session_id)

        #----Saving user's email in the current session to access database in other pages----#
        request.session['email']=str(email)
        short_mail = email[:email.index('@')]

    #----Checking user's role----#
    if short_mail in database.child('users').child('students').get().val():
        user_data = database.child('users').child('students').child(short_mail).get().val()
        request.session['role'] = 'students'
    elif short_mail in database.child('users').child('managers').get().val():
        user_data = database.child('users').child('managers').child(short_mail).get().val()
        request.session['role'] = 'managers'
    elif short_mail in database.child('users').child('staff').get().val():
        user_data = database.child('users').child('staff').child(short_mail).get().val()
        request.session['role'] = 'staff'

    #----Checking if any message needs to be displayed----#
    if request.session.get('msg'):
        user_data['msg'] = request.session.get('msg')
        del request.session['msg']

    #----Getting inventory from database----#
    inventory = database.child('Inventory').get().val()
    user_data['inventory'] = inventory

    #----Rendering home page based on user's role----#
    if request.session['role'] == 'students':  
        request = checkNotification(request, short_mail)  
        return render(request,"main_Student.html",user_data)
    elif request.session['role'] == 'managers':
        user_data['courses'] = database.child('Courses').get().val()
        return render(request,"main_Wmanager.html",user_data)
    elif request.session['role'] == 'staff':
        user_data['courses'] = database.child('Courses').get().val()
        user_data['students'] = database.child('users').child('students').get().val()
        for k, v in user_data['students'].items():
            user_data['students'][k].pop('password')
            if 'loaning' in v:
                user_data['students'][k].pop('loaning')
            if 'requirements' in v:
                user_data['students'][k].pop('requirements')
            if 'notify' in v:
                user_data['students'][k].pop('notify')

        return render(request,"main_ASM.html",user_data)

def login_page(request):
    #----Checking if there is already a user logged in----#
    if request.session.get('uid'):
        return redirect('/home')

    return render(request, 'login.html')

def logout(request):
    try:
        del request.session['uid']
        message = 'Successfully Logged Out!'
    except:
        pass
    return render(request, "login.html", {"message":message})

def main_Student(request): 
    return render(request, 'main_Student.html')

def main_ASM(request): 
    return render(request, 'main_ASM.html')

def create_user(request):
    full_name = "{} {}".format(request.POST.get('fname'),request.POST.get('lname'))
    num_id, role = int(request.POST.get('id')), int(request.POST.get('role'))
    email, password = request.POST.get('email'), request.POST.get('password')
    short_mail = email[:email.index('@')].lower()

    if short_mail not in database.child('users').child('students').get().val() \
    and short_mail not in database.child('users').child('staff').get().val() \
    and short_mail not in database.child('users').child('managers').get().val():
        if role == 1:
            #----Creating Student User in Database----#
            if request.POST.getlist('courses'):
                courses = request.POST.getlist('courses')
            else:
                courses = None
            authe.create_user_with_email_and_password(email, password)
            database.child('users').child('students').child(short_mail).set({
                'full_name': full_name,
                'id': num_id,
                'password': password,
            })
            if courses:
                database.child('users').child('students').child(short_mail).child('courses').set(courses)
            #----Creating Student User in Database----#
        elif role == 2:
            #----Creating Warehouse Manager User in Database----#
            authe.create_user_with_email_and_password(email, password)
            database.child('users').child('managers').child(short_mail).set({
                'full_name': full_name,
                'id': num_id,
                'password': password,
            })
            #----Creating Warehouse Manager User in Database----#
        elif role == 3:
            #----Creating Academic Staff Member User in Database----#
            authe.create_user_with_email_and_password(email, password)
            database.child('users').child('staff').child(short_mail).set({
                'full_name': full_name,
                'id': num_id,
                'password': password,
            })
            #----Creating Academic Staff Member User in Database----#
        request.session['msg'] = 'User {} was created successfully!'.format(full_name)
    else:
        request.session['msg'] = 'User already exists!'
    
    return redirect('/home')

def remove_user(request):
    email = request.POST.get('email')
    if email != request.session['email']:
        #----Checking which role is trying to remove a user ASM or WM----#
        if request.POST.get('staff'):
            flag = 0
        else:
            flag = 1   
        
        password = None
        short_mail = email[:email.index('@')]

        if short_mail in database.child('users').child('students').get().val():
            #----Checking if user is under Students in database----#
            full_name = database.child('users').child('students').child(short_mail).child('full_name').get().val()
            password = database.child('users').child('students').child(short_mail).child('password').get().val()
            role = 1
        elif short_mail in database.child('users').child('managers').get().val() and flag:
            #----Checking if user is under Warehouse Manager in database----#
            full_name = database.child('users').child('managers').child(short_mail).child('full_name').get().val()
            password = database.child('users').child('managers').child(short_mail).child('password').get().val()
            role = 2
        elif short_mail in database.child('users').child('staff').get().val() and flag:
            #----Checking if user is under Academic Staff Members in database----#
            full_name = database.child('users').child('staff').child(short_mail).child('full_name').get().val()
            password = database.child('users').child('staff').child(short_mail).child('password').get().val()
            role = 3
            
        if password:
            #----If user exists under one of the roles in the database----#
            #----Loging in to the user's account to get refreshed idToken----#
            user = authe.sign_in_with_email_and_password(email,password)
            #----Deleting the user from the database----#
            authe.delete_user_account(user['idToken'])

            #----Removing user info from the database based on his role----#
            if role == 1:
                database.child('users').child('students').child(short_mail).remove()
            elif role == 2:
                database.child('users').child('managers').child(short_mail).remove()
            elif role == 3:
                database.child('users').child('staff').child(short_mail).remove()
            request.session['msg'] = 'User {} was removed successfully!'.format(full_name)
        else:
            if not flag:
                request.session['msg'] = "User does not exist or you are trying to remove a user that is not a Student!"
            else:
                request.session['msg'] = "User does not exist!"
    else:
        request.session['msg'] = 'You cannot delete yourself!'

    return redirect('/home')

    

def inventory_stock(request):
    items = list()  
    role = request.session['role'] #role to know which table to render
    inventory = database.child('Inventory').get()
    filter = '0'
    bad_serial_token = "" 
    request.session['bad_serial'] = 0



# ======= Handling with the request type
    if 'InStock' in request.POST: 
        filter = request.POST['InStock'] 
    elif 'OutOfStock' in request.POST:
        filter = request.POST['OutOfStock'] 
    elif 'btn_save_edit' in request.POST:    
        editInventory(request)             
    elif 'btn_remove_edit' in request.POST: 
        removeInventory(request) 
    elif 'btn_save_new' in request.POST: 
        NewItemInventory(request)
    

    if request.session['bad_serial'] == -1:
        request.session['bad_serial'] = 0
        bad_serial_token = 'Serial Number does not exist!' 
    if request.session['bad_serial'] == -2:
        request.session['bad_serial'] = 0
        bad_serial_token = 'Serial Number already exist!'

#======================================= table for academic staff member ======================================
    if role == 'staff':
    #========InStock   
        if filter == '1': 
            for i in inventory.each(): 
                if database.child('Inventory').child(i.key()).child('Quantity').get().val() is not None:
                    if database.child('Inventory').child(i.key()).child('Quantity').get().val() > 0: 
                        product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                        product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
                        items.append((product_name,product_amount,role)) 

            return render(request, "inventory_stock_ASM.html", {'items':items})  
    #========OutOfStock
        if filter == '2': 
            for i in inventory.each(): 
                if database.child('Inventory').child(i.key()).child('Quantity').get().val() is not None:
                    if database.child('Inventory').child(i.key()).child('Quantity').get().val() == 0: 
                        product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                        product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
                        items.append((product_name,product_amount,role)) 

            return render(request, "inventory_stock_ASM.html", {'items':items})  
    #========ShowAll Case
        else: 
            for i in inventory.each():
                product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
                items.append((product_name,product_amount,role)) 
                
            return render(request, "inventory_stock_ASM.html", {'items':items}) 



#=======================================table for warehouse manager===========================================
    else:   
        #========InStock   
        if filter == '1': 
            for i in inventory.each(): 
                if database.child('Inventory').child(i.key()).child('Quantity').get().val() is not None:
                    if int(database.child('Inventory').child(i.key()).child('Quantity').get().val()) > 0:
                        product_serial = i.key() 
                        product_location = database.child('Inventory').child(i.key()).child('Physical_Location').get().val()
                        product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                        product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
                        items.append((product_name,product_amount,product_serial,product_location,role)) 

            return render(request, "inventory_stock_Manager.html", {'items':items})  
    #========OutOfStock
        if filter == '2':
            for i in inventory.each(): 
                if database.child('Inventory').child(i.key()).child('Quantity').get().val() is not None:
                    if int(database.child('Inventory').child(i.key()).child('Quantity').get().val()) == 0: 
                        product_serial = i.key() 
                        product_location = database.child('Inventory').child(i.key()).child('Physical_Location').get().val()
                        product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                        product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val() 

                        items.append((product_name,product_amount,product_serial,product_location,role))
                        
            return render(request, "inventory_stock_Manager.html", {'items':items})  
    #========ShowAll Case 
        else: 
            for i in inventory.each():
                product_serial = i.key() 
                product_location = database.child('Inventory').child(i.key()).child('Physical_Location').get().val()
                product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
                product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
                items.append((product_name,product_amount,product_serial,product_location,role)) 
                
            return render(request, "inventory_stock_Manager.html", {'items':items, 'error': bad_serial_token})



def editInventory(request):

    inventory = database.child('Inventory').get() 
    serial_number = request.POST['serial_number'] 
    serial_flag = False 
      
    # ======= check if serial number exist 
    for key in inventory.each(): 
        if int(serial_number) == int(key.key()): 
            serial_flag = True 
    
    if serial_flag == False: 
        request.session['bad_serial'] = -1 
      
    else:
        # ======= set the fields to user requset
        if request.POST['product_name'] != "":
            new_product_name = request.POST['product_name'] 
        else: 
            new_product_name = database.child('Inventory').child(serial_number).child('product_name').get().val()
        
        if request.POST['quantity'] != "":
            new_quantity = request.POST['quantity'] 
            #======= Notfiy students that the item is back in stock 
            if database.child('Inventory').child(serial_number).child('Quantity').get().val() < int(new_quantity):
                notifyStudents(request) 
        else: 
            new_quantity = database.child('Inventory').child(serial_number).child('Quantity').get().val()

        if request.POST['product_location'] != "":
            new_product_location = request.POST['product_location']  
        else: 
            new_product_location = database.child('Inventory').child(serial_number).child('Physical_Location').get().val()
        

        # =========== updating DB      
        database.child('Inventory').child(serial_number).update({'product_name': new_product_name})
        database.child('Inventory').child(serial_number).update({'Physical_Location': new_product_location})  
        database.child('Inventory').child(serial_number).update({'Quantity': int(new_quantity)}) 
                    
        return render(request,"inventory_stock_Manager.html")


    
def removeInventory(request):  
    

    inventory = database.child('Inventory').get() 
    serial_number = request.POST['serial_number'] 
    serial_flag = False 
    
    # ======= Check if serial number exist 
    for key in inventory.each(): 
        if int(serial_number) == int(key.key()): 
            serial_flag = True 

    # ======= Add a message to appear on the page   
    if serial_flag == False: 
        request.session['bad_serial'] = -1  
    # ======= Removing the item from database 
    else:  
        database.child('Inventory').child(serial_number).remove() 
        return render(request,"inventory_stock_Manager.html")
    


def send_requirements(request):
    requirements = {}
    quantity = request.POST.getlist("quantity")
    #----Removing all empty or 0 values from quantities----#
    i = 0
    while "" in quantity or "0" in quantity:
        if quantity[i] == "" or quantity[i] == "0":
            quantity.pop(i)
        else:
            i+=1

    #----Creating dictionary with course name as key and quantities as value----#
    for k in request.POST.getlist("reqBox"):
        if quantity:
            requirements[k] = int(quantity[0])
            quantity.pop(0)

    course = database.child("Courses").child(request.POST.get("course"))
    course.child("requirements").set(requirements)

    request.session['msg'] = "Requirements for course " + request.POST.get("course") + " have been sent!"
    
    return redirect('/home')

def NewItemInventory(request): 
    
    inventory = database.child('Inventory').get() 
    serial_number = request.POST['serial_number'] 
    serial_flag = False 
      
    # ======= check if serial number exist 
    for key in inventory.each(): 
        if int(serial_number) == int(key.key()):  
            serial_flag = True
        
    # ======= add certain msg to be shown on page
    if serial_flag == True: 
        request.session['bad_serial'] = -2
    # ======= saving the new item attributes on local variable
    else:  
        new_product_name = request.POST['product_name']
        new_quantity = request.POST['quantity'] 
        new_product_location = request.POST['product_location']
        new_consumable = request.POST['consumable']

    # ======= new item attributes as a dictionary
        data = { 
            'product_name': new_product_name,
            'Physical_Location': new_product_location, 
            'Quantity': int(new_quantity),
            'Consumable': new_consumable
        }
    # ======= Adding to database
        database.child('Inventory').child(serial_number).update(data)
                 
    return render(request,"inventory_stock_Manager.html")




#----------------------------------------------US3 ASM order submition--------------------

def submit_an_order_ASM(request):
        
        return render(request,"submit_an_order_ASM.html")



def remove_from_course(request):
    #----Getting all courses and the students posted from the form----#
    courses = request.POST.getlist("courseRemove")
    student = request.POST.get("student")

    #----Getting the courses of the selcted student from the database----#
    student_courses = database.child('users').child('students').child(student).child('courses').get().val()

    #----Creating new list with all courses that were not selected in the form posted----#
    student_courses = [course for course in student_courses if course not in courses]
    
    #----Updating courses for the student with the new list that was created----#
    database.child('users').child('students').child(student).child('courses').set(student_courses)

    full_name = database.child('users').child('students').child(student).get().val()['full_name']

    request.session['msg'] = full_name + " was removed from courses " + str(courses)
    return redirect('/home')

def student_courses(request):
    email = request.session['email']
    name = email[:email.index("@")]
    items = list()
    flag = 0
    courses_list = list()
    courses_db = database.child('users').child('students').child(name).child('courses').get()
    all_courses = database.child('Courses').get()

    for c in courses_db.each():
        if c is not None:
            courses_list.append(c.val())
    for c in all_courses.each():
        c_name = c.key()
        if c_name is not None:
            if c_name in courses_list:
                flag = 1
                name_w_pdf = f'{c_name} requirements list.pdf'
                current_dir = f'{os.getcwd()}\{name_w_pdf}'
                pdf_data = []
                products = database.child('Courses').child(c_name).child('requirements').get()
                for p in products.each():
                    if p is not None:
                        pdf_data.append((p.key(), p.val()))
                
                new_file = Canvas(name_w_pdf)
                new_file.setFont('Courier-Bold', 12)
                image = f'{os.getcwd()}/app/static/SCE_logo.png'
                new_file.drawCentredString(300, 720, name_w_pdf[:name_w_pdf.index(".")])
                new_file.setFont('Courier', 12)
                width, height = 110,50
                new_file.drawImage(image, (A4[0] - width) / 2, 750, width=width, height=height, mask = 'auto')
                text = new_file.beginText(60, 680)
                for line in pdf_data:
                    text.textLine(f'{line[0]}: {line[1]}')
                new_file.drawText(text)
                new_file.save()
                storage1.child(name_w_pdf).put(current_dir, name_w_pdf)
                os.remove(f"{name_w_pdf}")
                bucket = storage.bucket()
                blob = bucket.blob(name_w_pdf)
                signed_url = blob.generate_signed_url(
                    version='v4',
                    expiration=timedelta(hours=1),
                    method='GET'
                )
                items.append((c_name, signed_url))
    return render(request, "student_courses.html", {'items':items})


def ordering_existing_items_table(request):
   #-----------This part of the function is for checking if there is an existing order on the session user, if it does exist the user will be redirect to home/
    orders_ID=database.child('orders').get()
    user_mail=request.session['email']
    short_mail = user_mail[:user_mail.index('@')]
    user_id=str(database.child('users').child('staff').child(short_mail).child('id').get().val()) 
    for i in orders_ID.each():
        if(user_id == database.child('orders').child(i.key()).get().key()):
            request.session['msg'] = "you already orderd! please wait until your order approved"
            return redirect ('/home')
    #-----------end of checking ---------------------------------------------------
    items = list()  
    inventory = database.child('Inventory').get()
    for i in inventory.each():
        if(database.child('Inventory').child(i.key()).child('Quantity').get().val()==0 or database.child('Inventory').child(i.key()).child('Quantity').get().val()==""):
            product_name = database.child('Inventory').child(i.key()).child('product_name').get().val()
            #product_amount = database.child('Inventory').child(i.key()).child('Quantity').get().val()
            items.append((product_name)) 
                  
    return render(request, "ordering_existing_items_ASM.html", {'items':items}) 

def  ordering_existing_items_request(request): #------This function running only if the user dont have any previous orders waiting
    orders_ID=database.child('orders').get()
    user_mail=request.session['email']
    short_mail = user_mail[:user_mail.index('@')]
    user_id=str(database.child('users').child('staff').child(short_mail).child('id').get().val()) 
    
    new_order_branch={'date':0,'order details':{},'role':3,'status':'pending'}
    database.child('orders').child(user_id).update(new_order_branch)
    items=request.POST.getlist("reqBox")
    inventory=database.child('Inventory').get()
    Amount = request.POST.getlist("Amount")
    i = 0
    while "" in Amount or "0" in Amount:
        if Amount[i] == "" or Amount[i] == "0":
            Amount.pop(i)
        else:
            i+=1
    data_dict={}
    for n in range(len(items)):
        data_dict[items[n]] = int(Amount[n])       
    database.child('orders').child(user_id).child('order details').set(data_dict)    
    return redirect('/home')

def order_status(request):
    user_mail=request.session['email']
    short_mail = user_mail[:user_mail.index('@')]
    user_id=str(database.child('users').child('staff').child(short_mail).child('id').get().val()) 
    Status_existing=str(database.child('orders').child(user_id).child('status').get().val())
    Status_new=str(database.child('order_new_items').child(user_id).child('status').get().val())
    if(Status_existing=="pending" or Status_new=="pending"):
        return render(request,'submit_an_order_ASM.html',{"msg2":"Your order is awaiting confirmation"})
    elif(Status_existing=="approved" or Status_new=="approved"):
        return render(request,'submit_an_order_ASM.html',{"msg2":"Your order Approved"}) 
    else:
        return render(request,'submit_an_order_ASM.html',{"msg2":"You haven't ordered anything yet"})
    

def ordering_new_items(request):
    
    new_orders_ID=database.child('order_new_items').get()
    user_mail=request.session['email']
    short_mail = user_mail[:user_mail.index('@')]
    user_id=str(database.child('users').child('staff').child(short_mail).child('id').get().val())
    for i in new_orders_ID.each():
        if(user_id == database.child('order_new_items').child(i.key()).get().key()):
            return render(request,'submit_an_order_ASM.html',{"msg2":"you already orderd! please wait until your order approved"})
    
    if request.POST.get("comment"):
        status={'status':'pending','items':request.POST.get("comment")}
        database.child('order_new_items').child(user_id).set(status)
        return redirect('/home')
    return render(request,'ordering_new_items.html')

def student_ordering(request):
    email = request.session['email']
    short_mail = email[:email.index('@')]
    user_data = database.child('users').child('students').child(short_mail).get().val()
    uid = user_data['id']
    inventory = database.child('Inventory').get().val()


    if request.POST.get('courseFilter'):
        course = request.POST.get('courseFilter')
    elif request.POST.get('course'):
        course = request.POST.get('course')
    elif 'courses' in user_data:
        course = user_data['courses'][0]
    else:
        course = None
    user_data['course'] = course

    #----Checking if submit order button was pressed----#
    if request.POST.get('order'):
        order_details = dict(zip(request.POST.getlist('items'), request.POST.getlist('amount')))
        order_details = {k: int(v) for k,v in order_details.items()}
        order = {'date': str(date.today()), 'order details': order_details, 'role': 1, 'status': 'approved'}
        orders = database.child('orders').get().val()

        #----Checking if user already made an order----#
        if str(uid) in orders:
            for item in order_details:
                #----If user already ordered the item for another course, update the order quantity----#
                if item in orders[str(uid)]['order details']:
                    current = orders[str(uid)]['order details'][item]
                    up = {item: int(order_details[item]) + int(current)}
                    database.child('orders').child(uid).child('order details').update(up)
                else:
                    database.child('orders').child(uid).child('order details').update({item: order_details[item]})
        #----Else create a new order in the database with user's ID----#
        else:
            database.child('orders').child(uid).set(order)

        #----Update user's database with items that were ordered for the course----#
        database.child('users').child('students').child(short_mail).child('requirements').child(course).update(order_details)

        #----Updating inventory stocks in the database----#
        for k, i in inventory.items():
            if i['product_name'] in order_details:
                #----Incase an item needs loaning, the item will be added to the student's database with date of loaning and return by date----#
                if i['Consumable'] == '0':
                    student = database.child('users').child('students').child(short_mail)
                    student.child('loaning').child(i['product_name']).update({'Quantity': order_details[i['product_name']],
                                                                              'Date': str(date.today()),
                                                                              'Return': str(date(2023,1,19))})
                database.child('Inventory').child(k).update({'Quantity': i['Quantity'] - order_details[i['product_name']]})

        #----If an item was out-of-stock and the student checked the notification checkbox, add the item to his database for notifications----#
        if request.POST.get('notify'):
            notify = request.POST.getlist('notify')
            notify = {x : inventory[x]['product_name'] for x in notify}
            database.child('users').child('students').child(short_mail).child('notify').update(notify)


        #----Pull new data from user's database----#
        user_data = database.child('users').child('students').child(short_mail).get().val()
        user_data['course'] = course
    
    if course:
        #----Pulling course requirements from the database----#
        requirements = database.child('Courses').child(course).child('requirements').get().val()
        user_data['req'] = {}

        #----If user have any loaned items, check if they are needed for this course----#
        #----if so remove that item from the course requirements and set as ordered in database----#
        if 'loaning' in user_data:
            for item in dict(requirements):
                if item in user_data['loaning'] and course not in user_data['requirements']:
                    add = {item: 1}
                    database.child('users').child('students').child(short_mail).child('requirements').child(course).update(add)
                    requirements.pop(item)
                elif item in user_data['loaning'] and item not in user_data['requirements'][course]:
                    add = {item: 1}
                    database.child('users').child('students').child(short_mail).child('requirements').child(course).update(add)
                    requirements.pop(item)

        #----Check if student already ordered some items for this course----#
        if 'requirements' in user_data:
            if course in user_data['requirements']:
                if dict(requirements) == user_data['requirements'][course]:
                    user_data['filled'] = True
                    return render(request, "student_ordering.html", user_data)
                else:
                    for k in dict(requirements):
                        if k in user_data['requirements'][course] and requirements[k] == user_data['requirements'][course][k]:
                            requirements.pop(k)
                        elif k in user_data['requirements'][course]:
                            requirements[k] = int(requirements[k]) - int(user_data['requirements'][course][k])

        #----Create requirements dictionary to send to the ordering page----#
        for k in requirements:
            for s, i in inventory.items():
                if i['product_name'] == k:               
                    user_data['req'][k] = {'quantity': requirements[k],
                                        'available_quantity': i['Quantity'],
                                        'loan': i['Consumable'],
                                        'serial': s,}
                    break

    return render(request, "student_ordering.html", user_data) 



def notifyStudents(request): 
    serial_number = request.POST['serial_number']
    student_list = database.child('users').child('students').get()
    

    for student in student_list.each():  
        field = student.val() 
             
        #======= Checking if student marked this item to be notified
        if 'notify' in field:  
            if serial_number in field['notify']: 
                user_name = field['full_name'].split()[0]     

        #======= Updating in student database the item is now avilable       
                database.child('users').child('students').child(user_name).child('notify').update({serial_number:'Is Back In Stock'}) 
    
def checkNotification(request, user_name): 
    notifications = database.child('users').child('students').child(user_name).child('notify').get()
    dict = {} 
    loan_dict =  {}
    
    if notifications.val() == None:  
        request.session['notify'] = dict
        return request

    for item in notifications.each(): 
        if 'Back In Stock' in item.val():
            product_name = database.child('Inventory').child(item.key()).child('product_name').get().val()
            if product_name != None:
                dict[product_name] = item.val()

    request.session['notify'] = dict 
    # --------------------- notifications about loaned items --------------------- #
    loan_items = database.child('users').child('students').child(user_name).child('loaning').get().val()
    if loan_items is not None:
        today = datetime.datetime.today()
        for i in loan_items:
            in_date = loan_items[i]['Return']
            in_year = int(in_date[0:4])
            in_month = int(in_date[5:7])
            in_day = int(in_date[8:])
            return_date = datetime.datetime(year=in_year, month=in_month, day=in_day)
            delta = return_date - today
            if delta.days <= 3:
                loan_dict[i] = delta.days
        request.session['loan_items'] = loan_dict
        print(request.session['loan_items'])
            

    return request 

def pickup(request):
    month_dict = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
    max_days_to_show = 10
    days_list = list()
    hours_list = list()
    email = request.session['email']
    name = email[:email.index("@")]
    id = str(database.child('users').child(request.session['role']).child(name).child('id').get().val())
    all_orders = database.child('orders').get().val()
    print(all_orders)
    if id in all_orders:
        this_order = all_orders.get(id)
        if this_order["status"] == "approved":
            if this_order["date"] == 0:
                today = datetime.date.today()
                day = today.day + 1
                month = today.month
                year = today.year
                update_schedule_db(year)
                count = 1
                for d in range(day, monthrange(year, month)[1] + 1):
                    obj = datetime.datetime(year=year, month=month, day=d)
                    if obj.weekday() <= 3 or obj.weekday() == 6:
                        x = f'{d}.{month}'
                        days_list.append(x)
                if len(days_list) < max_days_to_show:
                    day = 1
                    month += 1
                    if month == 13:
                        year += 1
                        update_schedule_db(year)
                    while len(days_list) != max_days_to_show:
                        obj = datetime.datetime(year=year, month=month, day=d)
                        if obj.weekday() <= 3 or obj.weekday() == 6:
                            x = f'{d}.{month}'
                            days_list.append(x)
                if request.POST.get('days'):
                    answer = str(request.POST.get('days'))
                    picked_day = answer[:answer.index(".")]
                    month_num = int(answer[answer.index(".")+1:])
                    picked_month = month_dict[month_num-1]
                    hours = database.child('Schedule').child(year).child(picked_month).child(picked_day).get().val()
                    if hours != None:
                        for h in hours:
                            if hours[h] == 0:
                                hours_list.append(h)
                    request.session['hours_list'] = hours_list
                    if request.POST.get('hour'):
                        picked_hour = request.POST.get('hour')
                        database.child('orders').child(id).update({'date':f'{picked_day}{picked_month}{year} {picked_hour}'})
                        database.child('orders').child(id).update({'status':'scheduled'})
                        database.child('Schedule').child(year).child(picked_month).child(picked_day).update({picked_hour: id})
            else:
                request.session['msg'] = 'pickup is already scheduled for this order'
                return redirect('/home')
        else:
            request.session['msg'] = f'your order is {this_order["status"]}'
            return redirect('/home')
    else:
        request.session['msg'] = 'no order in the system'
        return redirect('/home')               

    return render(request, "pickup.html", {'days_list':days_list, 'hours_list':hours_list}) 
                          
 
def update_schedule_db(year1):
    dates = database.child('Schedule').get().val()
    if dates is not None:
        if year1 in dates:
            return
    else:
        times = {}
        for hour in range(10, 18):
            minuts = 0
            for i in range(0, 4):
                if minuts < 10:
                    times[f'{hour}:0{minuts}'] = 0
                else:
                    times[f'{hour}:{minuts}'] = 0
                minuts = minuts + 15
        month_dict = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
        for m in range(1, 13):
            days = list()
            for d in range(1, monthrange(year1, m)[1] + 1):
                obj = datetime.datetime(year=year1, month=m, day=d)
                if obj.weekday() <= 3 or obj.weekday() == 6:
                    days.append(d)
        
            for x in days:            
                database.child('Schedule').child(year1).child(month_dict[m-1]).child(str(x)).set(times)       
            days.clear()