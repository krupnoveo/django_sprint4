from django import forms
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from .models import Comment, Post

User = get_user_model()

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
        initial=now
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'image', 'pub_date', 'location']
