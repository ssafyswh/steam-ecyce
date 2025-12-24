# community/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    # ModelViewSet에서 저장 로직을 커스텀할 때는 perform_create를 씁니다.
    def perform_create(self, serializer):
        print('저장 시도 - perform_create 실행')
        serializer.save(user=self.request.user)
        