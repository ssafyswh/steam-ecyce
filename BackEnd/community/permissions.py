# community/permissions.py
from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 조회(GET, HEAD, OPTIONS)는 모두에게 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 수정, 삭제는 작성자(obj.user)와 요청자(request.user)가 같아야 함
        return obj.user == request.user