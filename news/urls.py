from django.urls import path
from .views import PostsList, PostsDetail, search_results, PostCreateView, PostUpdateView, PostDeleteView, home  # импортируем наше представление

app_name = 'news'

urlpatterns = [
    # path -- означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно почему
    path('', PostsList.as_view()),
    path('', PostsList.as_view(), name='all_news'),
    path('<int:pk>/', PostsDetail.as_view(), name='news'),
    path('search/', search_results, name='search_results'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/update/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('home/', home, name='home')


    # т.к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
]
