from django import forms
from .models import Blog,BlogComment


class BlogForm(forms.ModelForm):
    '''creating forms for the fields written in Blog model'''
    date_of_publish =forms.DateField(

        widget=forms.TextInput(attrs={
            'id':'datepicker',
        })
    )
    class Meta:
        model=Blog
        fields=('main_title','single_line_body','date_of_publish',
        'image','seo_title','seo_description','seo_keyword')


class CommentForm(forms.ModelForm):
    '''creating forms for the fields written in Blog model'''
    class Meta:
        model=BlogComment
        fields=('first_name','last_name','email_id','comment')
