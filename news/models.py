from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django import forms
from datetime import datetime

from django.template.loader import render_to_string
from django.utils.html import strip_tags


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


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    # categories = models.ManyToManyField(Category, through='PostCategory')

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    ALLINONE = 'AL'
    POLICY = 'PL'
    SCIENCE = 'SC'
    TECH = 'TE'
    ART = 'AR'
    SPACE = 'SP'
    POST_CATEGORY_CHOICES = (
        (ALLINONE, 'Обо всем'),
        (POLICY, 'Политика'),
        (SCIENCE, 'Наука'),
        (TECH, 'Технологии'),
        (ART, 'Искусство'),
        (SPACE, 'Космос'),
    )

    name = models.CharField(max_length=100, default='None')

    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    postCategory = models.CharField(max_length=2, choices=POST_CATEGORY_CHOICES, default=ALLINONE)
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

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'postCategory']

class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)


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
