from django import forms
from django.forms import ModelForm
""" Import from local app. """
from .models import CategoryModel
from .models import ArticleModel


""" start category form here. """
# start CategoryForm here.
class CategoryForm(ModelForm):

    class Meta:
        model   = CategoryModel

        fields  = ['serial', 'title', 'description', 'status']

        labels  = {
            'serial': 'Post number',
            'title': 'Category title',
            'description': 'Category description',
            'status': 'Status'
        }

        widgets = {
            'serial': forms.NumberInput(attrs={'class': 'form-control rounded-0', 'type': 'numbers'}),
            'title': forms.TextInput(attrs={'type': 'text', 'class': 'form-control rounded-0', 'placeholder':'Category title'}),
            'status': forms.Select(attrs={'class': 'custom-select rounded-0'}),
            'description': forms.Textarea(attrs={'type': 'text', 'rows': '5', 'class': 'form-control border-0 rounded-0', 'placeholder':'Article description'})
        }


""" start article form here. """
# article form.
class ArticleForm(ModelForm):

    class Meta:
        model = ArticleModel

        fields = [ 'serial', 'cover_image', 'title', 'category', 'description',
                   'shortlines', 'content', 'status', 'total_views', 'verification',
                   'is_promote', 'is_trend' ]

        labels = { 'serial': 'Serial Number',
                   'cover_image': 'Cover image',
                   'title': 'Title',
                   'category': 'Category',
                   'description': 'Description',
                   'shortlines': 'Shortlines',
                   'content': 'Content',
                   'status': 'Status',
                   'total_views': 'Total views',
                   'verification': 'Verify',
                   'is_promote': 'Promote',
                   'is_trend': 'Trend', }

        widgets = { 'serial': forms.NumberInput(attrs={'class': 'form-control rounded-0', 'type': 'numbers'}),
                    'cover_image': forms.FileInput(attrs={'type': 'file', 'class': 'custom-file-input rounded-0'}),
                    'title': forms.TextInput(attrs={'type': 'text', 'class': 'form-control rounded-0','placeholder':'Article title'}),
                    'status': forms.Select(attrs={'class': 'custom-select rounded-0'}),
                    'category': forms.Select(attrs={'class': 'custom-select rounded-0'}),
                    'description': forms.Textarea(attrs={'type': 'text', 'class': 'form-control border-0 rounded-0', 'rows': '5', 'placeholder':'Article description'}),
                    'shortlines': forms.Textarea(attrs={'type': 'text', 'class': 'form-control border-0 rounded-0', 'rows': '5', 'placeholder':'Article shortlines'}),
                    'content': forms.Textarea(attrs={'type': 'text', 'class': 'form-control border-0 rounded-0', 'id': 'mytextarea', 'rows': '20', 'placeholder':'Article content'}),
                    'total_views': forms.NumberInput(attrs={'class': 'form-control rounded-0', 'type': 'numbers'}),
                    'verification': forms.CheckboxInput(attrs={}),
                    'is_promote': forms.CheckboxInput(attrs={}),
                    'is_trend': forms.CheckboxInput(attrs={})
                  }