from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import Post, Author, Category
from django import forms
from allauth.account.forms import SignupForm
# Создаём модельную форму
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'author', 'title', 'categoryType', 'postCategory', 'text']
        labels = {
            'name': 'Название',
            'author': 'Автор',
            'title': 'Заголовок',
            'categoryType': 'Категория',
            'postCategory': 'Категория поста',
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
            'postCategory': forms.SelectMultiple(attrs={
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
        self.fields['postCategory'].queryset = Category.objects.all()
        self.fields['postCategory'].label_from_instance = lambda obj: obj.name


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                label='Пароль')
    password2 = forms.CharField(max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                label='Подтвердите пароль')

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )
        labels = {
            'username': 'Имя',
            'email': 'Почта',
            'password1': 'Пароль',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # 'password1': forms.PasswordInput(attrs={'class': 'form-control'}), # Для паролей виджет не работает. Чтобы задать атрибуты, например, название класса, следует использовать поле модели, как показано выше.
            # 'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return super().clean()

class LoginForm(AuthenticationForm):
    class Meta:
       model = User
       fields = (
         "username",
         "password",
           )


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get_or_create(name='common')[0]
        basic_group.user_set.add(user)
        return user
