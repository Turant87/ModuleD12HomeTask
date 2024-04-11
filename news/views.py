# from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.views import View
from django.core.paginator import Paginator
from .models import Post, Comment
from django.utils import timezone
from django.core.cache import cache
from .filters import NewsFilter
from django.shortcuts import render
from .forms import PostForm, Author
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


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
   success_url = reverse_lazy('news:all_news')

   # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
   def get_object(self, **kwargs):
       id = self.kwargs.get('pk')
       return Post.objects.get(pk=id)

class PostDeleteView(DeleteView):
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

class PostCreateView(CreateView):
   template_name = 'news/post_create.html'
   form_class = PostForm
   success_url = reverse_lazy('news:all_news')








