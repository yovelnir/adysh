from django.test import TestCase
import time
from django.conf import settings
from .views import *
from django.http import HttpRequest
from django.conf import settings
from importlib import import_module 




db = firebase.database()
auth = firebase.auth()

class LoginPageTest(TestCase):
    def test_login_page(self):
        request = HttpRequest()
        request.session = {}
        request.session['uid'] = None
        self.assertEqual(login_page(request).status_code, 200, "Login page not working")

class LogOutTest(TestCase):
    def test_logout(self):
        request = HttpRequest()
        request.session = {}
        request.session['uid'] = '12345678'
        self.assertEqual(logout(request).status_code, 200, "Login page not working")
        self.assertEqual(request.session.get('uid'), None, "User session still exists!")

class StudentTestCase(TestCase):
    def test_student_login(self):
        request = HttpRequest()
        request.session = {}
        request.session['uid'] = None

        request.POST['email'] = 'student@test.com'
        request.POST['password'] = '123456'

        response = postLogin(request)
        self.assertEqual(response.status_code, 200)

class StaffTestCase(TestCase):
    def test_student_login(self):
        request = HttpRequest()
        request.session = {}
        request.session['uid'] = None

        request.POST['email'] = 'staff@test.com'
        request.POST['password'] = '123456'

        response = postLogin(request)
        self.assertEqual(response.status_code, 200)

class ManagerTestCase(TestCase):
    def test_student_login(self):
        request = HttpRequest()
        request.session = {}
        request.session['uid'] = None

        request.POST['email'] = 'manager@test.com'
        request.POST['password'] = '123456'

        response = postLogin(request)
        self.assertEqual(response.status_code, 200)

class ManageUsers(TestCase):

    def test_create_student(self):
        request = HttpRequest()
        request.session = {}

        request.POST['email'] = 'studenttest@test.test'
        request.POST['fname'] = 'student'
        request.POST['lname'] = 'test'
        request.POST['password'] = '123456'
        request.POST['id'] = 123456789
        request.POST['role'] = 1

        response = create_user(request)
        self.assertEqual(response.status_code, 302)

        user_data = db.child('users').child('students').child('studenttest').get().val()
        self.assertTrue(user_data, 'User was not created correctly in database!')
        self.assertEqual(user_data['id'], request.POST['id'])
        self.assertEqual(user_data['full_name'], '{} {}'.format(request.POST['fname'], request.POST['lname']))
        self.assertEqual(user_data['password'], request.POST['password'])

    def test_create_staff(self):
        request = HttpRequest()
        request.session = {}

        request.POST['email'] = 'stafftest@test.test'
        request.POST['fname'] = 'staff'
        request.POST['lname'] = 'test'
        request.POST['password'] = '123456'
        request.POST['id'] = 123456789
        request.POST['role'] = 3

        response = create_user(request)
        self.assertEqual(response.status_code, 302)

        user_data = db.child('users').child('staff').child('stafftest').get().val()
        self.assertTrue(user_data, 'User was not created correctly in database!')
        self.assertEqual(user_data['id'], request.POST['id'])
        self.assertEqual(user_data['full_name'], '{} {}'.format(request.POST['fname'], request.POST['lname']))
        self.assertEqual(user_data['password'], request.POST['password'])

    def test_create_manager(self):
        request = HttpRequest()
        request.session = {}

        request.POST['email'] = 'managertest@test.test'
        request.POST['fname'] = 'manager'
        request.POST['lname'] = 'test'
        request.POST['password'] = '123456'
        request.POST['id'] = 123456789
        request.POST['role'] = 2

        response = create_user(request)
        self.assertEqual(response.status_code, 302)

        user_data = db.child('users').child('managers').child('managertest').get().val()
        self.assertTrue(user_data, 'User was not created correctly in database!')
        self.assertEqual(user_data['id'], request.POST['id'])
        self.assertEqual(user_data['full_name'], '{} {}'.format(request.POST['fname'], request.POST['lname']))
        self.assertEqual(user_data['password'], request.POST['password'])

    def test_remove_student(self):
        request = HttpRequest()
        request.session = {}
        request.session['email'] = None
        request.POST['email'] = 'studenttest@test.test'

        response = remove_user(request)
        self.assertEqual(response.status_code, 302)

        user_data = db.child('users').child('students').child('studenttest').get().val()
        self.assertFalse(user_data, 'User was not removed from the database!')
        
    def test_remove_staff(self):
        request = HttpRequest()
        request.session = {}
        request.session['email'] = None
        request.POST['email'] = 'stafftest@test.test'

        response = remove_user(request)
        self.assertEqual(response.status_code, 302)

        user_data = db.child('users').child('staff').child('stafftest').get().val()
        self.assertFalse(user_data, 'User was not removed from the database!')

    def test_remove_manager(self):
        request = HttpRequest()
        request.session = {}
        request.session['email'] = None
        request.POST['email'] = 'managertest@test.test'

        response = remove_user(request)
        self.assertEqual(response.status_code, 302)

        user_data = db.child('users').child('staff').child('managertest').get().val()
        self.assertFalse(user_data, 'User was not removed from the database!')
    
    def test_remove_student_course(self):
        db.child('users').child('students').child('student').child('courses').update({0: 'test1',})
        request = HttpRequest()
        request.session = {}
        request.POST['student'] = 'student'
        request.POST['courseRemove'] = 'test1'

        response = remove_from_course(request)
        self.assertEqual(response.status_code, 302)
        data = db.child('users').child('students').child('student').child('courses').get().val()
        self.assertFalse(data, "courses were not removed from database!")

        
class Requirements(TestCase):
    def test_send_requirements(self):
        request = HttpRequest()
        request.session = {}

        request.POST['reqBox'] = 'Camera'
        request.POST['quantity'] = 1
        request.POST['course'] = 'test_course'

        response = send_requirements(request)
        self.assertEqual(response.status_code, 302)

        data = db.child('Courses').child('test_course').child('requirements').get().val()
        self.assertTrue(data, "requirements were not sent!")
        self.assertEqual(data[request.POST['reqBox']], request.POST['quantity'])
        db.child('Courses').child('test_course').remove()


class ViewInventory(TestCase):  
    def test_Inventory_Staff(self):
            response = self.client.get('inventory_stock_ASM/') 
            self.assertEquals(response.status_code, 404)
            

    def test_Inventory_Manager(self):   
        #======= check Warehouse Manager page
        response = self.client.get('inventory_stock_Manager/') 
        self.assertEquals(response.status_code, 404)


    def test_remove_inventory(self):    
        
        #======= Helper functions 
        def add_item_to_database(self):
            db.child('Inventory').child('-1').set({'name': 'testCase', 'quantity': -1})  

        def get_item_from_database(self):
            item = db.child('Inventory').child('-1').get()
            if item is None:
                return None
            return {'serial_number': '-1', 'name': 'name', 'quantity': -1} 
        #======= End of helper functions
            
        #======= Test removing an item that exists in the database
        request = HttpRequest()
        request.POST['serial_number'] = -1
        add_item_to_database(self)
        response = removeInventory(request)
        self.assertEqual(response.status_code, 200)
        item = get_item_from_database(self)
        self.assertIsNot(item, None)

    def test_NewItemInventory(self):   
        request = HttpRequest()     

        request.POST['product_name'] = 'testCase'
        request.POST['quantity'] = -1
        request.POST['product_location'] = 'testCase'
        request.POST['consumable'] = 'testCase' 
        request.POST['serial_number'] = -1 

        response = NewItemInventory(request)
        self.assertEqual(response.status_code, 200)
        removeInventory(request)


    def test_editInventory(self):   
        request = HttpRequest()  
        #======= Saving the real value 
        realQuantity = db.child('Inventory').child('101').child('Quantity').get().val()

        #====== The field we would like to test is Quantity
        request.POST['product_name'] = ''
        request.POST['quantity'] = -1
        request.POST['product_location'] = ''
        request.POST['consumable'] = '' 
        request.POST['serial_number'] = 101  

        editInventory(request) 

        #======= Getting the updated value 
        editedQuantity = db.child('Inventory').child('101').child('Quantity').get().val() 
        db.child('Inventory').child(101).update({'Quantity': realQuantity})
        
        self.assertEqual(editedQuantity, -1) 


class test_notifyStudents(TestCase):  

    def test_notify_students(self): 
        item_data = { 
            'product_name': 'adivtest',
            'Physical_Location': 'testCase', 
            'Quantity': int(0), 
        } 
        student_data = { 
            'full_name':'adivtest adiv', 
            'id':'123456789',
            'notify': {'-1':'testCase'},
            'password':'123456',
        }
    
        database.child('Inventory').child(-1).update(item_data)
        database.child('users').child('students').child('adivtest').update(student_data)  

        request = HttpRequest() 
        request.POST['serial_number'] = '-1' 
        notifyStudents(request)

        msg = database.child('users').child('students').child('adivtest').child('notify').child(-1).get().val()
        
        self.assertEqual('Is Back In Stock',msg) 

        database.child('users').child('students').child('adivtest').remove()
        database.child('Inventory').child(-1).remove()




     

        





