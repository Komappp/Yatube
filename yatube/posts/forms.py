from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta(ModelForm):
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    class Meta(ModelForm):
        model = Comment
        fields = ('text',)
