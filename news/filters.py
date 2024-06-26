import django_filters
from .models import Post, Category
from django.contrib.auth.models import User

class NewsFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='dateCreation', lookup_expr='gte', label='После даты')
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='По названию')
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all(), field_name='author__authorUser__username', lookup_expr='icontains', label='По автору')
    postCategory = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='postCategory',
        to_field_name='name',
        label='По категории'
    )


    class Meta:
        model = Post
        fields = ['date', 'title', 'author', 'postCategory']
