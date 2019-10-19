from rest_framework import generics
from django.db.models import Q
from rest_framework import filters
from ..models import CategoryModelScheme
from ..models import ArticleModelScheme
from .api_serializers import CategorySchemeSerializer
from .api_serializers import ArticleSchemeSerializer
from .api_permissions import IsOwnerOrReadOnly


class CategoryListViewset(generics.ListAPIView):
    queryset = CategoryModelScheme.objects.all()
    serializer_class = CategorySchemeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'description')
    ordering_fields = ('serial',)


class CategoryRetrieveViewset(generics.RetrieveAPIView):
    queryset = CategoryModelScheme.objects.all()
    serializer_class = CategorySchemeSerializer
    lookup_field = 'slug'


class CategoryUpdateViewset(generics.RetrieveUpdateAPIView):
    queryset = CategoryModelScheme.objects.all()
    serializer_class = CategorySchemeSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]


class CategoryDestroyViewset(generics.DestroyAPIView):
    queryset = CategoryModelScheme.objects.all()
    serializer_class = CategorySchemeSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]


class CategoryCreateViewset(generics.CreateAPIView):
    queryset = CategoryModelScheme.objects.all()
    serializer_class = CategorySchemeSerializer

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)


class ArticleListViewset(generics.ListAPIView):
    queryset = ArticleModelScheme.objects.all()
    serializer_class = ArticleSchemeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'description')
    ordering_fields = ('serial',)


class ArticleRetrieveViewset(generics.RetrieveAPIView):
    queryset = ArticleModelScheme.objects.all()
    serializer_class = ArticleSchemeSerializer
    lookup_field = 'slug'


class ArticleUpdateViewset(generics.RetrieveUpdateAPIView):
    queryset = ArticleModelScheme.objects.all()
    serializer_class = ArticleSchemeSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]


class ArticleDestroyViewset(generics.DestroyAPIView):
    queryset = ArticleModelScheme.objects.all()
    serializer_class = ArticleSchemeSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]


class ArticleCreateViewset(generics.CreateAPIView):
    queryset = ArticleModelScheme.objects.all()
    serializer_class = ArticleSchemeSerializer

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)
