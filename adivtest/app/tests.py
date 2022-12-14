from django.test import TestCase
from .views import firebase

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
        student = auth.sign_in_with_email_and_password(email, passw)
        student_data = db.child('users').child(email[:email.index('@')]).get().val()

        #Check if the user is really looged in
        self.assertTrue(auth.current_user)
        #Checking if user data is equal to db data
        self.assertEqual(student['idToken'], auth.current_user['idToken'], "It is the same user!")
        self.assertEqual(student_data['role'], 3, "User should be role 3 (academic staff member)")
        
auth.current_user = None