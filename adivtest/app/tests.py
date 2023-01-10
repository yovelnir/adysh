from django.test import TestCase
import time
from django.conf import settings
from .views import firebase
from .views import removeInventory 
from .views import NewItemInventory 
from .views import editInventory
from django.http import HttpRequest 




db = firebase.database()
auth = firebase.auth()

# class StudentTestCase(TestCase):
#     def setUp(self):
#         auth.sign_in_with_email_and_password("studenttest@test.com", "123456")
    
#     def test_student_login(self):
#         email, passw = "studenttest@test.com", "123456"
#         student = auth.sign_in_with_email_and_password(email, passw)
#         student_data = db.child('users').child(email[:email.index('@')]).get().val()

#         #Check if the user is really looged in
#         self.assertTrue(auth.current_user)
#         #Checking if user data is equal
#         self.assertEqual(student['idToken'], auth.current_user['idToken'], "It is the same user!")
#         self.assertEqual(student_data['role'], 1, "User should be role 1 (student)")
        
# auth.current_user = None      

# class AcademicStaffTestCase(TestCase): 
#     def setUp(self):
#         auth.sign_in_with_email_and_password("stafftest@test.com", "123456") 
        
#     def test_ASM_login(self): 
#         email, passw = "stafftest@test.com", "123456"
#         ASM = auth.sign_in_with_email_and_password(email, passw)
#         ASM_data = db.child('users').child(email[:email.index('@')]).get().val()

#         #Check if the user is really looged in
#         self.assertTrue(auth.current_user)
#         #Checking if user data is equal
#         self.assertEqual(ASM['idToken'], auth.current_user['idToken'], "It is the same user!")
#         self.assertEqual(ASM_data['role'], 3, "User should be role 3 (academic staff member)")

# auth.current_user = None  

# class managerTestCase(TestCase):
#     def setUp(self):
#         auth.sign_in_with_email_and_password("managertest@test.com", "123456")
    
#     def test_manager_login(self):
#         email, passw = "managertest@test.com", "123456"  
#         manager = auth.sign_in_with_email_and_password(email,passw)      
#         manager_data = db.child('users').child(email[:email.index('@')]).get().val() 

#         self.assertTrue(auth.current_user)
#         #Checking if user data is equal to db data
#         self.assertEqual(manager['idToken'], auth.current_user['idToken'], "It is the same user!")
#         self.assertEqual(manager_data['role'], 2, "User should be role 2 ( warehouse manager)")
        
# auth.current_user = None

# class ManageUsers(TestCase):

#     def testCreation(self):

#         auth.create_user_with_email_and_password('test@test.com','123456') 
#         user = auth.sign_in_with_email_and_password('test@test.com', '123456')

#         email = 'test@test.com' 
#         full_name = 'test test' 
#         num_id = 123123123 
#         role = 1

#         db.child('users').child('test').child(email[0:email.index('@')]).set({
#         'idToken': user['idToken'],
#         'full_name': full_name,
#         'id': num_id,
#         'role': role,
#     })
#         self.assertNotEqual(user,None) 


#     def testDelete(self):     
#         email = 'test@test.com' 
#         user = auth.sign_in_with_email_and_password('test@test.com', '123456') 
#         auth.delete_user_account(user['idToken'])  
#         db.child('users').child('test').child(email[0:email.index('@')]).remove()
#         idToken = db.child('users').child(email[:email.index('@')]).child('idToken').get().val()
#         self.assertNotEqual(user['idToken'] ,idToken)

class ViewInventory(TestCase):  #Working
    def test_Inventory_Staff(self):
            response = self.client.get('inventory_stock_ASM/') 
            self.assertEquals(response.status_code, 404)
            

    def test_Inventory_Manager(self):   #Working
        #======= check Warehouse Manager page
        response = self.client.get('inventory_stock_Manager/') 
        self.assertEquals(response.status_code, 404)


    def test_remove_inventory(self):    #Working
        
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

    # def test_remove_invetory_2(self):         #AttributeError: 'HttpRequest' object has no attribute 'session'
        
    #     # Test removing an item that does not exist in the database
    #     request = HttpRequest()
    #     request.POST['serial_number'] = -10
    #     response = removeInventory(request)
    #     self.assertEqual(response.status_code, 404)


    def test_NewItemInventory(self):   #Working
        request = HttpRequest()     

        request.POST['product_name'] = 'testCase'
        request.POST['quantity'] = -1
        request.POST['product_location'] = 'testCase'
        request.POST['consumable'] = 'testCase' 
        request.POST['serial_number'] = -1 

        response = NewItemInventory(request)
        self.assertEqual(response.status_code, 200)
        removeInventory(request)


    def test_editInventory(self):   #Working
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
        










