from django.forms import ModelForm
from .models import Post, Author
from django import forms
# Создаём модельную форму
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'author', 'title', 'categoryType', 'text']
        labels = {
            'name': 'Название',
            'author': 'Автор',
            'title': 'Заголовок',
            'categoryType': 'Категория',
            'text': 'Текст',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название'
            }),
            'author': forms.Select(attrs={
                'class': 'form-control',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок'
            }),
            'categoryType': forms.Select(attrs={
                'class': 'form-control',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите текст'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()
        self.fields['author'].label_from_instance = lambda obj: obj.authorUser.username