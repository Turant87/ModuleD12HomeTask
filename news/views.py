from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views.decorators.cache import cache_page
from django.views.decorators.http import last_modified
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

@method_decorator(cache_page(60 * 5), name='dispatch')
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

    # def post(self, request, *args, **kwargs):
    #     # берём значения для нового продукта из POST-запроса, отправленного на сервер
    #     name = request.POST['name']
    #     title = request.POST['title']
    #     categoryType = request.POST['categoryType']
    #     postCategory = request.POST['postCategory']
    #     author_name = request.POST['author']
    #     author = get_object_or_404(Author, authorUser=author_name)
    #     text = request.POST['text']
    #     post = Post(author=author, name=name, title=title, categoryType=categoryType, postCategory=postCategory, text=text)  # создаём новый пост и сохраняем
    #     post.save()
    #     return super().get(request, *args, **kwargs)  # отправляем пользователя обратно на GET-запрос

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = get_object_or_404(Author, authorUser=request.user)
            post.save()
            form.save_m2m()  # Сохраняем связи многие-ко-многим
            return HttpResponseRedirect(post.get_absolute_url())
        return render(request, 'news/post_create.html', {'form': form})

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        if category_id:
            return Post.objects.filter(postCategory=category_id)
        return Post.objects.all()

    def create_post(request):
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)  # Создаем объект, но не сохраняем его в базе данных
                post.author = request.user.author  # Предполагается, что у пользователя есть связанный объект Author
                post.save()  # Теперь сохраняем объект в базе данных
                post.postCategory.set(form.cleaned_data['postCategory'])  # Сохраняем связанные категории
                return HttpResponseRedirect(post.get_absolute_url())
        else:
            form = PostForm()
        return render(request, 'create_post.html', {'form': form})


class PostsByCategory(ListView):
    model = Post
    template_name = 'news/posts_by_cat.html'
    context_object_name = 'posts'
    paginate_by = 8

    # def get_queryset(self):
    #     category_id = self.kwargs.get('id')  # Получаем значение по ключу 'id'
    #     category = get_object_or_404(Category, id=category_id)
    #     return Post.objects.filter(postCategory=category)
    def get_queryset(self):
        posts_by_category = Post.objects.filter(postCategory__id=self.kwargs['id'])
        return posts_by_category

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


def last_modified_func(post_pk):
    return Post.objects.get(pk=post_pk).dateModified

@method_decorator(cache_page(60 * 60 * 24), name='dispatch')  # Кэширование на 24 часа
@method_decorator(last_modified(last_modified_func), name='dispatch')
class PostsDetail(DetailView):
    model = Post
    template_name = 'news/news.html'  # Изменил имя шаблона
    context_object_name = 'post'

def search_results(request):
    news_filter = NewsFilter(request.GET, queryset=Post.objects.all())
    return render(request, 'news/search.html', {'filter': news_filter})

@cache_page(60)
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
    return render(request, 'news/posts_by_cat.html', {'category': category, 'posts': posts})

def subscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.subscribers.add(request.user)
    return redirect('posts_by_category', category_id=category_id)

@login_required
def subscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.subscribe(request.user)
    return redirect('news:all_news')  # перенаправление пользователя куда-либо после подписки
@login_required
def unsubscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.unsubscribe(request.user)
    return redirect('news:all_news')  # перенаправление пользователя куда-либо после отписки

def weekly_newsletter():
    today = timezone.localtime(timezone.now())
    last_week = today - timezone.timedelta(days=7)
    categories = Category.objects.all()

    for category in categories:
        posts = category.post_set.filter(dateCreation__range=(last_week, today))
        if posts.exists():
            for user in category.subscribers.all():
                subject = f'Weekly Newsletter - New Articles in {category.name}'
                html_message = render_to_string('news/weekly_newsletter.html', {'posts': posts, 'category': category})
                plain_message = strip_tags(html_message)
                from_email = 'From <turant.ivan@mail.ru>'
                to = user.email

                send_mail(subject, plain_message, from_email, [to], html_message=html_message)

@receiver(post_save, sender=User)
def welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Добро пожаловать в NewsPaper!'
        html_message = render_to_string('news/welcome_email.html', {'user': instance})
        plain_message = strip_tags(html_message)
        from_email = 'From <turant.ivan@yandex.ru>'
        to = instance.email

        send_mail(subject, plain_message, from_email, [to], html_message=html_message)