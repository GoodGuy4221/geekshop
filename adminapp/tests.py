from django.test import TestCase
from django.conf import settings
from django.test.client import Client

from authnapp.models import ShopUser


class TestUserManagement(TestCase):
    fixtures = [
        'mainapp/fixtures/001_categories.json',
        'mainapp/fixtures/002_products.json',
        'mainapp/fixtures/003_contact_locations.json',
        'authnapp/fixtures/admin_user.json',
    ]

    def setUp(self) -> None:
        self.client = Client()
        self.superuser = ShopUser.objects.create_superuser(username='django', password='django')
        self.user = ShopUser.objects.create_user(username='varick', password='varick')
        self.user_with__first_name = ShopUser.objects.create_user(
            username='james-bond', password='bond-007', first_name='bond'
        )

    def test_user_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(response.context['page_title'], 'Магазин - Главная')
        self.assertNotContains(response, 'Пользователь', status_code=200)
        # self.assertNotIn('Пользователь', response.content.decode())

        # Set user's data
        self.client.login(username='varick', password='varick')

        # Log in
        response = self.client.get('/auth/login/')
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertEqual(response.context['user'], self.user)

        # After log in
        response = self.client.get('/')
        self.assertContains(response, 'Пользователь', status_code=200)
        self.assertEqual(response.context['user'], self.user)

    # def test_user_with__first_name_login(self):
    #     self.client.login(username='james-bond', password='bond-007')
    #
    #     self.client.get('/auth/login/')
    #
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(self.user_with__first_name.first_name, response.content.decode())
    #
    # def test_superuser_login(self):
    #     self.client.login(username='django', password='django')
    #
    #     response = self.client.get('/auth/login/')
    #     self.assertEqual(response.context['user'].is_superuser, True)
    #
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('админка', response.content.decode())

    def test_basket_login_redirect(self):
        # Test without log in. Must be redirected.
        response = self.client.get('/basket/')
        self.assertEqual(response.url, '/auth/login/?next=/basket/')
        self.assertEqual(response.status_code, 302)

        self.client.login(username='varick', password='varick')

        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['basket']), [])
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['page_title'], 'корзина')
        self.assertEqual(response.request['PATH_INFO'], '/basket/')
        self.assertIn('Ваша корзина, Пользователь', response.content.decode())

    def test_user_logout(self):
        # User's data
        self.client.login(username='varick', password='varick')

        # Log in
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_anonymous)

        # Log out
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 302)

        # After log out
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(response.context['page_title'], 'Магазин - Главная')
        self.assertNotIn('Пользователь', response.content.decode())

    def test_user_register(self):
        response = self.client.get('/auth/register/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_title'], 'регистрация')
        self.assertTrue(response.context['user'].is_anonymous)

        new_user_data = {
            'username': 'cinderella',
            'first_name': 'cinderella',
            'last_name': 'cinderella',
            'password1': 'discombobulated',
            'password2': 'discombobulated',
            'age': '28',
        }

        # Create new user
        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEqual(response.status_code, 302)

        new_user = ShopUser.objects.get(username=new_user_data['username'])
        # print(new_user, new_user.activation_key)

        activation_url = f"{settings.DOMAIN_NAME}/auth/verify/{new_user_data['email']}/{new_user.activation_key}/"

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username=new_user_data['username'], password=new_user_data['password1'])

        # Log in
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_anonymous)

        # Main page check
        response = self.client.get('/')
        self.assertContains(response, text=new_user_data['first_name'], status_code=200)

    def test_user_wrong_register(self):
        new_user_data = {
            'username': 'baby',
            'first_name': 'baby',
            'last_name': 'baby',
            'password1': 'premonition',
            'password2': 'premonition',
            'age': '17',
        }

        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEqual(response.status_code, 200)
        # self.assertFormError(response, form, field, errors, msg_prefix='')
        self.assertFormError(response, 'register_form', 'age', 'Вы слишком молоды!')
        self.assertIn('Вы слишком молоды!', response.content.decode())
