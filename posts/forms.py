from django import forms
from .models import Blog
from django.contrib.auth.models import User

class BlogForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ['title', 'author', 'content', 'tags']

        widgets = {

            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Blog Title'
            }),

            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author Name'
            }),

            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, AI'
            }),

            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your blog content here...',
                'rows': 20,
                'style': 'min-height:500px; resize:vertical;'
            }),

        }


class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Password do not matched !!!!")

        return cleaned_data