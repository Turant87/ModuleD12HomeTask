from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django import forms
from django.contrib import admin
from datetime import datetime, timezone

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from prompt_toolkit.validation import ValidationError
from django.utils import timezone


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postRating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.all().aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories')

    def __str__(self):
        return self.name

    def subscribe(self, user):
        self.subscribers.add(user)
    def unsubscribe(self, user):
        self.subscribers.remove(user)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    name = models.CharField(max_length=100, default='None')

    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    # postCategory = models.CharField(max_length=2, choices=POST_CATEGORY_CHOICES, default=ALLINONE)
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'



    def __str__(self):
        return f'Post #{self.pk} - Name: {self.name}'

    def get_absolute_url(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
        return f'/post/{self.id}'

    def save(self, *args, **kwargs):
        today_min = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        today_max = timezone.localtime().replace(hour=23, minute=59, second=59, microsecond=999999)
        posts_today = Post.objects.filter(author=self.author, dateCreation__range=(today_min, today_max))

        if posts_today.count() >= 3:
            raise ValidationError('Вы не можете публиковать более трёх новостей в сутки.')
        super().save(*args, **kwargs)


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'categoryType', 'postCategory']
        widgets = {
            'postCategory': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['categoryType'].choices = Post.CATEGORY_CHOICES
        self.fields['postCategory'].queryset = Category.objects.all()
        self.fields['postCategory'].help_text = 'Удерживайте "Control" (или "Command" на Mac), чтобы выбрать более одной опции.'


    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            self.instance.postCategory.set(self.cleaned_data['postCategory'])
        return post


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.commentPost.author.authorUser.username

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя") # опционально, можно не указывать
    last_name = forms.CharField(label = "Фамилия") # опционально

    class Meta:
        model = User
        fields = ("username",
                  "first_name", # опционально
                  "last_name", # опционально
                  "email",
                  "password1",
                  "password2", )





