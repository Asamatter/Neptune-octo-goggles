from django import forms
from .models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'file', 'content']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['title']


class CommentForm(forms.ModelForm):
        class Meta:
            model = Comment 
            fields = ['content']
            exclude = ['user', 'poll', 'created_at' ]


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply 
        fields = ['content']        
