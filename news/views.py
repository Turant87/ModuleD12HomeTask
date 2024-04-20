# from django.shortcuts import render
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.core.paginator import Paginator
from .models import Post, Comment, Category
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
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.localtime(timezone.now())
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        context['form'] = PostForm()
        context['posts_with_categories'] = Post.objects.prefetch_related('categories')
        return context

    def post(self, request, *args, **kwargs):
        # берём значения для нового продукта из POST-запроса, отправленного на сервер
        name = request.POST['name']
        title = request.POST['title']
        categoryType = request.POST['categoryType']
        postCategory = request.POST['postCategory']
        author_name = request.POST['author']
        author = get_object_or_404(Author, authorUser=author_name)
        text = request.POST['text']
        post = Post(author=author, name=name, title=title, categoryType=categoryType, text=text)  # создаём новый пост и сохраняем
        post.save()
        return super().get(request, *args, **kwargs)  # отправляем пользователя обратно на GET-запрос

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        if category_id:
            return Post.objects.filter(postCategory=category_id)
        return Post.objects.all()

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = get_object_or_404(Author, authorUser=request.user)
            new_post.save()
            return HttpResponseRedirect(new_post.get_absolute_url())
        return super().get(request, *args, **kwargs)

class CategoryListView(ListView):
    model = Category
    template_name = 'news/category_list.html'  # Создайте соответствующий шаблон
    context_object_name = 'categories'



class PostUpdateView(UpdateView):
   template_name = 'news/post_update.html'
   model = Post
   form_class = PostForm
   login_url = '/login/'  # Укажите здесь ваш URL для входа, если он отличается
   redirect_field_name = 'redirect_to'
   success_url = reverse_lazy('news:all_news')

   # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
   def get_object(self, **kwargs):
       id = self.kwargs.get('pk')
       return Post.objects.get(pk=id)

class PostDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
   template_name = 'news/post_delete.html'
   queryset = Post.objects.all()
   success_url = reverse_lazy('news:all_news')
   permission_required = ('news.delete_post',)

   # def handle_no_permission(self):
   #     if self.raise_exception or self.request.user.is_authenticated:
   #         raise PermissionDenied(self.get_permission_denied_message())
   #     return redirect('news:login')

# Только автор может удалить пост
   # def get_object(self, queryset=None):
   #     obj = super(PostDeleteView, self).get_object()
   #     if not obj.author.authorUser == self.request.user:
   #         raise Http404
   #     return obj

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
   model = Post
   form_class = PostForm
   success_url = reverse_lazy('news:all_news')

class RegisterView(CreateView):
   model = User
   form_class = RegisterForm
   template_name = 'news/signup.html'
   success_url = 'news/user.html'

   def form_valid(self, form):
       user = form.save()
       group = Group.objects.get_or_create(name='common')[0]
       user.groups.add(group)  # добавляем нового пользователя в эту группу
       user.save()
       return super().form_valid(form)


class IndexView(TemplateView):
    template_name = 'news/home.html'
    form_class = PostForm


class UresView(LoginRequiredMixin, TemplateView):
    template_name = 'news/user.html'
    form_class = PostForm
    success_url = reverse_lazy('news:user')

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
    return redirect('news:user')



class LoginView(FormView):
   model = User
   form_class = LoginForm
   template_name = 'news/login.html'
   success_url = 'news/user.html'

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

def my_custom_permission_denied_view(request, exception):
    return render(request, 'news/403.html', status=403)



def posts_by_category(request, category_id):
    # Получаем категорию по ID и связанные с ней посты
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(postCategory=category)
    return render(request, 'news/posts_by_category.html', {'category': category, 'posts': posts})











