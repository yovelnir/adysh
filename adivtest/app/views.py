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
import os


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
storage = firebase.storage()

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

    if request.session.get('msg'):
        user_data['msg'] = request.session.get('msg')
        del request.session['msg']

    #----Rendering home page based on user's role----
    if request.session['role'] == 'students':
        return render(request,"main_Student.html",user_data)
    elif request.session['role'] == 'managers':
        return render(request,"main_Wmanager.html",user_data)
    elif request.session['role'] == 'staff':
        return render(request,"main_ASM.html",user_data)

def login_page(request):
    #----Checking if there is already a user logged in----
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
    #-----Getting current session user data-----#
    email = request.session['email']
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
                'full_name': full_name,
                'id': num_id,
                'password': password,
            })
        elif role == 2:
            user = authe.create_user_with_email_and_password(email, password)
            database.child('users').child('managers').child(short_mail).set({
                'full_name': full_name,
                'id': num_id,
                'password': password,
            })
        elif role == 3:
            user = authe.create_user_with_email_and_password(email, password)
            database.child('users').child('staff').child(short_mail).set({
                'full_name': full_name,
                'id': num_id,
                'password': password,
            })
        request.session['msg'] = 'User {} was created successfully!'.format(full_name)
    else:
        request.session['msg'] = 'User already exists!'
    
    return redirect('/home')

def remove_user(request):
    #-----Getting current session user data-----#
    email = request.session['email']
    user_data = database.child('users').child(request.session['role']).child(email[:email.index('@')]).get().val()
    #-----Getting current session user data-----#

    email = request.POST.get('email')
    if email != request.session['email']:
        password = None
        short_mail = email[:email.index('@')]
        if short_mail in database.child('users').child('students').get().val():
            full_name = database.child('users').child('students').child(short_mail).child('full_name').get().val()
            password = database.child('users').child('students').child(short_mail).child('password').get().val()
            role = 1
        elif short_mail in database.child('users').child('managers').get().val():
            full_name = database.child('users').child('managers').child(short_mail).child('full_name').get().val()
            password = database.child('users').child('managers').child(short_mail).child('password').get().val()
            role = 2
        elif short_mail in database.child('users').child('staff').get().val():
            full_name = database.child('users').child('staff').child(short_mail).child('full_name').get().val()
            password = database.child('users').child('staff').child(short_mail).child('password').get().val()
            role = 3
            
        if password:
            user = authe.sign_in_with_email_and_password(email,password)
            authe.delete_user_account(user['idToken'])

            if role == 1:
                database.child('users').child('students').child(short_mail).remove()
            elif role == 2:
                database.child('users').child('managers').child(short_mail).remove()
            elif role == 3:
                database.child('users').child('staff').child(short_mail).remove()
            request.session['msg'] = 'User {} was removed successfully!'.format(full_name)
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



    if 'InStock' in request.POST: 
        filter = request.POST['InStock'] 
    elif 'OutOfStock' in request.POST:
        filter = request.POST['OutOfStock'] 
    elif 'btn_save_edit' in request.POST: 
        editInventory(request)             
    elif 'btn_remove_edit' in request.POST: 
        removeInventory(request) 
    
    if request.session['bad_serial'] == -1:
        request.session['bad_serial'] = 0
        bad_serial_token = 'Serial Number does not exist!'

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
        if int(serial_number) == key.key(): 
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
      
    # ======= check if serial number exist 
    for key in inventory.each(): 
        if serial_number == key.key(): 
            serial_flag = True
    
    if serial_flag == False: 
        request.session['bad_serial'] = -1  

    else:  
        database.child('Inventory').child(serial_number).remove() 
        return render(request,"inventory_stock_Manager.html")
    


def student_courses(request):
    email = request.session['email']
    name = email[:email.index("@")]

    items = list()
    courses_list = list()
    courses_db = database.child('users').child('students').child(name).child('courses').get()
    for c in courses_db.each():
        if c is not None:
            courses_list.append(c.val())
    all_courses = database.child('Courses').get()
 

    for c in all_courses.each():
        c_name = c.key()
        if c_name is not None:
            if c_name in courses_list:
                
                # creating pdf file
                pdf_data = []
                products = database.child('Courses').child(c.key()).child('requirements').get()
                for p in products.each():
                    if p is not None:
                        pdf_data.append((p.key(), p.val()))
                name = f'{c_name} requierments list.pdf'
                new_file = Canvas(name)
                new_file.setFont('Helvetica', 14)
                new_file.setTitle('Requiermants list')
                new_file.drawCentredString(300, 750, name[:name.index(".")])
                text = new_file.beginText(60, 720)
                current_dir = os.getcwd()
                current_dir = f'{current_dir}\{name}'
                for line in pdf_data:
                    text.textLine(f'{line[0]}: {line[1]}')
                new_file.drawText(text)
                new_file.save()

                #pdf_path = 'adysh-d6408.appspot.com/requirements list'
                storage.child('pdf files').put(current_dir, name)
                items.append((c_name, (p.key(), p.val())))
    return render(request, "student_courses.html", {'items':items})
