from django.test import TestCase
from ..forms import SignUpForm

class SignUpFormTest(TestCase):
    def setUp(self):
        self.form = SignUpForm()

    def test_form_has_fields(self):
        expected_fields = ['username', 'email', 'password1', 'password2']
        actual_fields = list(self.form.fields)
        self.assertListEqual(expected_fields, actual_fields, "Form fields do not match expected fields")
