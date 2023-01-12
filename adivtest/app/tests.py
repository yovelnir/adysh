from django.test import TestCase
from .views import firebase
from .views import *

db = firebase.database()
auth = firebase.auth()

class StudentTestCase(TestCase):
    def setUp(self):
        auth.sign_in_with_email_and_password("studenttest@test.com", "123456")
    
    def test_student_login(self):
        email, passw = "studenttest@test.com", "123456"
        student = auth.sign_in_with_email_and_password(email, passw)
        student_data = db.child('users').child(email[:email.index('@')]).get().val()

        #Check if the user is really looged in
        self.assertTrue(auth.current_user)
        #Checking if user data is equal
        self.assertEqual(student['idToken'], auth.current_user['idToken'], "It is the same user!")
        self.assertEqual(student_data['role'], 1, "User should be role 1 (student)")
        
auth.current_user = None      

class AcademicStaffTestCase(TestCase): 
    def setUp(self):
        auth.sign_in_with_email_and_password("stafftest@test.com", "123456") 
        
    def test_ASM_login(self): 
        email, passw = "stafftest@test.com", "123456"
        ASM = auth.sign_in_with_email_and_password(email, passw)
        ASM_data = db.child('users').child(email[:email.index('@')]).get().val()

        #Check if the user is really looged in
        self.assertTrue(auth.current_user)
        #Checking if user data is equal
        self.assertEqual(ASM['idToken'], auth.current_user['idToken'], "It is the same user!")
        self.assertEqual(ASM_data['role'], 3, "User should be role 3 (academic staff member)")

auth.current_user = None  

class managerTestCase(TestCase):
    def setUp(self):
        auth.sign_in_with_email_and_password("managertest@test.com", "123456")
    
    def test_manager_login(self):
        email, passw = "managertest@test.com", "123456"  
        manager = auth.sign_in_with_email_and_password(email,passw)      
        manager_data = db.child('users').child(email[:email.index('@')]).get().val() 

        self.assertTrue(auth.current_user)
        #Checking if user data is equal to db data
        self.assertEqual(manager['idToken'], auth.current_user['idToken'], "It is the same user!")
        self.assertEqual(manager_data['role'], 2, "User should be role 2 ( warehouse manager)")
        
auth.current_user = None

class ManageUsers(TestCase):

    def testCreation(self):

        auth.create_user_with_email_and_password('test@test.com','123456') 
        user = auth.sign_in_with_email_and_password('test@test.com', '123456')

        email = 'test@test.com' 
        full_name = 'test test' 
        num_id = 123123123 
        role = 1

        db.child('users').child(email[0:email.index('@')]).set({
        'idToken': user['idToken'],
        'full_name': full_name,
        'id': num_id,
        'role': role,
    })
        self.assertNotEqual(user,None) 


    def testDelete(self):     
        email = 'test@test.com' 
        user = auth.sign_in_with_email_and_password('test@test.com', '123456') 
        auth.delete_user_account(user['idToken']) 
        db.child('users').child(email[0:email.index('@')]).remove()
        idToken = db.child('users').child(email[:email.index('@')]).child('idToken').get().val()
        self.assertNotEqual(user['idToken'] ,idToken)

class ViewInventory(TestCase):
    def test_Inventory_Is_Empty_Staff(self):
            Prod=db.child('Inventory').child('1').child('Quantity').get().val()
            self.assertNotEqual(Prod,None)

    def test_Inventory_Is_Equal_Manager(self): 
        #need to be implemented !
        return False

class OrderNewItemASM(TestCase):
    def test_if_order_submmited(self):
        ordering_new_items("aaa")
        order=db.child('orders').child('user_id').get().key()
        self.assertFalse(order,None)    

class OrderExisting_item(TestCase):
    def test_if_order_submitted(self):
        ordering_existing_items_request({'camera':2})
        order=db.child('orders').child('user_id').get()
        self.assertIsNotNone(order)