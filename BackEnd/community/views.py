# community/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404  # [추가] get_object_or_404 필요
from .models import Article, Comment, Review
from .serializers import ArticleSerializer, CommentSerializer, ReviewSerializer
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

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        프론트엔드에서 ?game_id=... 파라미터를 보낼 경우,
        현재 로그인한 유저가 해당 게임에 작성한 리뷰만 필터링하여 반환합니다.
        """
        queryset = super().get_queryset()
        game_id = self.request.query_params.get('game_id')
        
        # game_id가 쿼리 파라미터로 들어온 경우 필터링 수행
        if game_id is not None:
            # 현재 로그인한 유저의 리뷰만 조회 (수정용 데이터를 찾기 위함)
            # serializers.py에서 appid를 기준으로 조회했으므로 game__appid를 사용합니다.
            queryset = queryset.filter(game__appid=game_id, user=self.request.user)
            
        return queryset

    def perform_create(self, serializer):
        # 신규 등록 시 현재 로그인한 유저 정보를 저장
        serializer.save(user=self.request.user)