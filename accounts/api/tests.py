from testing.testcases import TestCase
from rest_framework import status
from rest_framework.test import APIClient

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        # This function will be executed before each test function executes
        self.client = APIClient()
        self.user = self.create_user(
            username = 'tester',
            email = 'tester@gmail.com',
            password = 'correct password',
        )

    def test_login_with_get_method_failed(self):
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_login_post_wrong_username_failed(self):
        response = self.client.post(LOGIN_URL, {
            'username': 'notexists',
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        print('response.data ==>\n{}'.format(response.data))

        self.assertEqual(response.data['errors']['username'][0],
                         'User does not exist.')

    def test_login_post_wrong_password_failed_login_status_as_false(self):
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_login_with_cap_username_success(self):
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username.upper(),
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_success_login_status_as_true(self):
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'tester@gmail.com')

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


    def test_logout(self):
        # login first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # validate login status as True
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # logout with get method not post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # use post successful logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validate login status as False
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': 'any password',
        }
        # Test get request failed
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # Test the wrong email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test password is too short
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test username is too long
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@gmail.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Successfully registered
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'someone')

        # Verify that the user is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)