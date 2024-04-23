from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views
from .views import PostsList, PostsDetail, search_results, PostCreateView, PostUpdateView, PostDeleteView, home, RegisterView,subscribe, unsubscribe, IndexView, upgrade_me, UresView, CategoryListView, PostsByCategory# импортируем наше представление

app_name = 'news'





urlpatterns = [
    # path('', PostsList.as_view()),
    path('', PostsList.as_view(), name='all_news'),
    path('<int:pk>/', PostsDetail.as_view(), name='news'),
    path('search/', search_results, name='search_results'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/update/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('home/', home, name='home'),
    # path('home/', IndexView.as_view(), name='home'),
    # path('index/', IndexView.as_view()),
    path('login/', LoginView.as_view(template_name='news/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='news/logout.html'), name='logout'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('user/', UresView.as_view(), name='user'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    # path('category/<int:category_id>/', PostsList.as_view(), name='posts_by_category'),
    # path('category/<int:category_id>/', PostsByCategory.as_view(), name='posts_by_category'),
    path('category/<int:category_id>/', views.posts_by_category, name='posts_by_category'),
    path('subscribe/<int:category_id>/', subscribe, name='subscribe'),
    path('unsubscribe/<int:category_id>/', unsubscribe, name='unsubscribe'),
]



    # т.к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view

