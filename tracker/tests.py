from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Transaction
from decimal import Decimal

class ExpenseTrackerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lucky', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        self.client = Client()
        self.category = Category.objects.create(user=self.user, name="Food")

    # --- Model Tests ---

    # 1) category creatiion -> 
    #  checks if the category created in setup actually hase name "Food"

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Food")


    # 2) Transaction creation  -->
    # creates a transaction for "Lunch" and checks if amount saved is exactly 50.00
    # confirms DecimalField is working properly 

    def test_transaction_creation(self):
        t = Transaction.objects.create(
            user=self.user, category=self.category, 
            amount=Decimal('50.00'), type='EXPENSE', description="Lunch"
        )
        self.assertEqual(t.amount, Decimal('50.00'))



    # 3) category string represntation -->
    # it checks __str__ method. whether it stores category name in admin panel as string or not

    def test_category_str_representation(self):
        self.assertEqual(str(self.category), "Food")



    # 4)  transaction string represntation -->
    # it checks __str__ method. whether it stores transaction name in admin panel as string or not

    def test_transaction_str_representation(self):
        t = Transaction.objects.create(user=self.user, category=self.category, amount=10, type='INCOME')
        self.assertTrue("INCOME" in str(t))



    # 5) caltegory test -->
    # it verifies two users can have same category

    def test_category_unique_per_user(self):
        # User 1 can have "Food", User 2 can also have "Food"
        Category.objects.create(user=self.other_user, name="Food")
        self.assertEqual(Category.objects.filter(name="Food").count(), 2)



    # 6) transaction date field -->
    # this checks date field is being filled even is user dont provide one 

    def test_transaction_default_date(self):
        t = Transaction.objects.create(user=self.user, category=self.category, amount=5, type='EXPENSE')
        self.assertIsNotNone(t.date)



    # 7) transaction linked to uers --> 
    # it checks when user create a transaction it linked to correct user 

    def test_transaction_linked_to_user(self):
        t = Transaction.objects.create(user=self.user, category=self.category, amount=5, type='EXPENSE')
        self.assertEqual(t.user.username, 'lucky')



    # 8) decimal precision -->
    # it checks 99.99 doest not change to 100 or something else, it ensure Decimal field is working properly 

    def test_decimal_precision(self):
        t = Transaction.objects.create(user=self.user, category=self.category, amount=Decimal('99.99'), type='EXPENSE')
        self.assertEqual(t.amount, Decimal('99.99'))




     # --- View Tests ---


    # 9) login required -->
    # if checks if user tries to visit dashboard without logging
    # it checks for 302 status code -> redirect to login

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login



    # 10) Logs in as lucky and then visits the dashboard. It expects a 200 status code, meaning "OK" or "Success."

    def test_dashboard_loads_for_logged_in_user(self):
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)





    # 11) Logs in and visits the category page. It checks that the response contains the string "Food," ensuring the content you expect is actually being rendered on the page.

    def test_category_list_view(self):
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Food")



    # 12) This is a Security Test. 
    # It creates a "Secret" category belonging to other_user. 
    # It then logs in as lucky and checks that "Secret" does not appear. 
    # This proves one user can't "snoop" on another's categories.

    def test_privacy_other_user_categories_hidden(self):
        Category.objects.create(user=self.other_user, name="Secret")
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('category_list'))
        self.assertNotContains(response, "Secret")





    # 13) Simply confirms the "Add Expense/Income" page is active and accessible for a logged-in user.
     
    def test_add_transaction_page_loads(self):
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('add_transaction'))
        self.assertEqual(response.status_code, 200)




    # 14 & 15) Confirms that your entry points (login and registration) are working correctly for anonymous visitors.

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
 

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)





    # 16) Logs in and then hits the logout URL. It checks for a 302 redirect, confirming the user is successfully kicked out of the session.

    def test_logout_redirect(self):
        self.client.login(username='lucky', password='password123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)





    # 17)  Another Security Test. 
    # It creates a transaction owned by other_user and tries to delete it while logged in as lucky. 
    # Expecting a 404 or 403 ensures lucky cannot manipulate data they don't own.

    def test_delete_transaction_permission_denied(self):
        t = Transaction.objects.create(user=self.other_user, category=self.category, amount=10, type='EXPENSE')
        self.client.login(username='lucky', password='password123')
        # Assuming you have a URL like 'delete_transaction' with id
        response = self.client.post(reverse('delete_transaction', args=[t.id]))
        self.assertEqual(response.status_code, 404) # Or 403 depending on your view logic






    # 18) Verifies that the edit form for a transaction loads correctly when given a valid transaction ID.

    def test_update_transaction_page_loads(self):
        t = Transaction.objects.create(user=self.user, category=self.category, amount=10, type='EXPENSE')
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('update_transaction', args=[t.id]))
        self.assertEqual(response.status_code, 200)






    # 19) Creates 15 transactions. It then specifically requests ?page=2. This confirms your pagination logic is working and you can successfully navigate through multiple pages of data.

    def test_pagination_on_dashboard(self):
        # Create 15 transactions to trigger pagination if set at 10
        for i in range(15):
            Transaction.objects.create(user=self.user, category=self.category, amount=i, type='EXPENSE')
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('dashboard') + '?page=2')
        self.assertEqual(response.status_code, 200)






    # 20) Tests the "No transactions found" UI. 
    # It verifies that when a user has no data, they see a helpful message rather than a broken page or a blank screen.

    def test_empty_dashboard_message(self):
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "You have no transactions yet. Add one to get started!")







    # --- CRUD & Functional Logic ---
    def test_successful_transaction_post(self):
        self.client.login(username='lucky', password='password123')
        response = self.client.post(reverse('add_transaction'), {
            'category': self.category.id,
            'amount': '100.50',
            'type': 'EXPENSE',
            'description': 'Rent',
            'date': '2026-02-21'
        })
        self.assertEqual(Transaction.objects.count(), 1)

    def test_invalid_transaction_post(self):
        self.client.login(username='lucky', password='password123')
        response = self.client.post(reverse('add_transaction'), {'amount': 'not-a-number'})
        # Should return to the form with errors
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(Transaction.objects.count(), 0)

    def test_delete_transaction_success(self):
        t = Transaction.objects.create(user=self.user, category=self.category, amount=10, type='EXPENSE')
        self.client.login(username='lucky', password='password123')
        self.client.post(reverse('delete_transaction', args=[t.id]))
        self.assertEqual(Transaction.objects.count(), 0)

    def test_add_category_via_post(self):
        self.client.login(username='lucky', password='password123')
        self.client.post(reverse('category_list'), {'name': 'Travel'})
        self.assertTrue(Category.objects.filter(name='Travel').exists())

    def test_dashboard_filtering_by_date(self):
        Transaction.objects.create(user=self.user, category=self.category, amount=10, type='EXPENSE', date='2025-01-01')
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('dashboard') + '?start_date=2026-01-01')
        self.assertNotContains(response, "10.00")


    def test_search_functionality(self):
        Transaction.objects.create(user=self.user, category=self.category, amount=10, type='EXPENSE', description="UniqueItem")
        self.client.login(username='lucky', password='password123')
        response = self.client.get(reverse('dashboard') + '?q=UniqueItem')
        self.assertContains(response, "UniqueItem")


    def test_password_mismatch_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'baduser', 'password': 'pass1', 'confirm_password': 'pass2'
        })
        self.assertFalse(User.objects.filter(username='baduser').exists())        