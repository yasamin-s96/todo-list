from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Task, User, Category


class TaskForm(forms.ModelForm):
    # overriding init to enable dynamic category choices
    def __init__(self, user_categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = user_categories

    class Meta:
        model = Task
        fields = ["content", "category", "task_due", "is_complete"]


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ["email"]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords do not match")
        return cd["password2"]


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["content"]
