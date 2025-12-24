# community/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Articles, ArticleImage
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Articles.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # ModelViewSet에서 저장 로직을 커스텀할 때는 perform_create를 씁니다.
    def perform_create(self, serializer):
        print('저장 시도 - perform_create 실행')
        
        # 1. 게시글 저장 (User 정보 주입)
        # 여기서 request.user를 넣어주지 않으면 "NOT NULL constraint failed" (500 에러) 발생
        article = serializer.save(user=self.request.user)
        
        # 2. 이미지 처리
        images = self.request.FILES.getlist('images')
        for img in images:
            ArticleImage.objects.create(article=article, image=img)