# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.core.paginator import Paginator
from .models import Post, Comment
from django.utils import timezone
from django.core.cache import cache
from .filters import NewsFilter
from django.shortcuts import render
from .forms import PostForm, Author, RegisterForm, LoginForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


class PostsList(ListView):
    model = Post
    template_name = 'news/all_news.html'  # Изменил имя шаблона
    context_object_name = 'posts'
    form_class = PostForm # Изменил на множественное число
    ordering = ['-dateCreation']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.localtime(timezone.now())
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        # берём значения для нового продукта из POST-запроса, отправленного на сервер
        name = request.POST['name']
        title = request.POST['title']
        categoryType = request.POST['categoryType']
        author_name = request.POST['author']
        author = get_object_or_404(Author, authorUser=author_name)
        text = request.POST['text']
        post = Post(author=author, name=name, title=title, categoryType=categoryType, text=text)  # создаём новый пост и сохраняем
        post.save()
        return super().get(request, *args, **kwargs)  # отправляем пользователя обратно на GET-запрос

class PostUpdateView(UpdateView):
   template_name = 'news/post_update.html'
   form_class = PostForm
   login_url = '/login/'  # Укажите здесь ваш URL для входа, если он отличается
   redirect_field_name = 'redirect_to'
   success_url = reverse_lazy('news:all_news')

   # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
   def get_object(self, **kwargs):
       id = self.kwargs.get('pk')
       return Post.objects.get(pk=id)

class PostDeleteView(LoginRequiredMixin, DeleteView):
   template_name = 'news/post_delete.html'
   queryset = Post.objects.all()
   success_url = reverse_lazy('news:all_news')

class PostsDetail(DetailView):
    model = Post
    template_name = 'news/news.html'  # Изменил имя шаблона
    context_object_name = 'post'

def search_results(request):
    news_filter = NewsFilter(request.GET, queryset=Post.objects.all())
    return render(request, 'news/search.html', {'filter': news_filter})

def home(request):
    # Здесь может быть логика для получения данных, которые вы хотите отобразить на домашней странице
    return render(request, 'news/home.html')  # Указываете шаблон для домашней страницы

class PostCreateView(LoginRequiredMixin, CreateView):
   template_name = 'news/post_create.html'
   form_class = PostForm
   success_url = reverse_lazy('news:all_news')

class RegisterView(CreateView):
   model = User
   form_class = RegisterForm
   template_name = 'news/signup.html'
   success_url = '/'

   def form_valid(self, form):
       user = form.save()
       group = Group.objects.get_or_create(name='common')[0]
       user.groups.add(group)  # добавляем нового пользователя в эту группу
       user.save()
       return super().form_valid(form)

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'news/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        print(f"is_not_authors: {context['is_not_authors']}")
        return context

@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')



class LoginView(FormView):
   model = User
   form_class = LoginForm
   template_name = 'news/login.html'
   success_url = '/'

   def form_valid(self, form):
       username = form.cleaned_data.get('username')
       password = form.cleaned_data.get('password')
       user = authenticate(self.request, username=username, password=password)
       if user is not None:
           login(self.request, user)
       return super().form_valid(form)


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'news/logout.html'
    success_url = '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)










