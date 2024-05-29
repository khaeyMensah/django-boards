from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

class LoginRequiredPasswordChangeTests(TestCase):
    def test_redirection(self):
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')

class PasswordChangeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
        cls.url = reverse('password_change')

    def setUp(self):
        self.client.login(username='john', password='old_password')

    def post_password_change(self, data):
        return self.client.post(self.url, data)

class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    def setUp(self):
        super().setUp()
        self.response = self.post_password_change({
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })

    def test_redirection(self):
        """A valid form submission should redirect the user."""
        self.assertRedirects(self.response, reverse('password_change_done'))

    def test_password_changed(self):
        """Refresh the user instance from database to get the new password hash updated by the change password view."""
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self):
        """Create a new request to an arbitrary page. The resulting response should now have a `user` to its context, after a successful sign up."""
        response = self.client.get(reverse('home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

class InvalidPasswordChangeTests(PasswordChangeTestCase):
    def setUp(self):
        super().setUp()
        self.response = self.post_password_change({
            'old_password': 'wrong_old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })

    def test_status_code(self):
        """An invalid form submission should return to the same page."""
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_didnt_change_password(self):
        """Refresh the user instance from the database to make sure we have the latest data."""
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))
