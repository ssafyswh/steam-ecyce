# community/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404  # [추가] get_object_or_404 필요
from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    # ModelViewSet에서 저장 로직을 커스텀할 때는 perform_create를 씁니다.
    def perform_create(self, serializer):
        print('저장 시도 - perform_create 실행')
        serializer.save(user=self.request.user)
        
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        # [수정] get_object_hash_or_404 -> get_object_or_404 (오타 수정)
        article_id = self.request.data.get('article')
        article = get_object_or_404(Article, pk=article_id)
        
        # 시리얼라이저의 save 메서드에 user와 article 객체를 넘겨줍니다.
        serializer.save(user=self.request.user, article=article)