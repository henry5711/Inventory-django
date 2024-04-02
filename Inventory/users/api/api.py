from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from users.models import User, Role
from users.api.serializers import UserSerializer, RoleSerializer

class UserIndexAPIView(APIView):
    pagination_class = PageNumberPagination
    def get(self, request):
        try:
            users = User.objects.all()
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(users, request)
            users_serializer = UserSerializer(result_page, many=True)
            return paginator.get_paginated_response(users_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserStoreAPIView(APIView):
    def post(self, request):
        try:
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserShowAPIView(APIView):
    def get(self, request, pk=None):
        try:
            user = User.objects.filter(id=pk).first()
            if user:
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
class UserUpdateAPIView(APIView):
    def put(self, request, pk=None):
        try:
            user = User.objects.filter(id=pk).first()
            if user:
                user_serializer = UserSerializer(user, data=request.data)
                if user_serializer.is_valid():
                    user_serializer.save()
                    return Response(user_serializer.data)
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDeleteAPIView(APIView):
    def delete(self, request, pk=None):
        try:
            user = User.objects.filter(id=pk).first()
            if user:
                user.delete()
                return Response({"message": "User deleted successfully"})
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserRestoreAPIView(APIView):
    def get(self, request, pk=None):
        try:
            user = User.objects.filter(id=pk, deleted_at__isnull=False).first()
            if user:
                user.deleted_at = None
                user.save()
                return Response({"message": "User restored successfully"})
            return Response({"error": "User not found or already restored"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleIndexAPIView(APIView):
    def get(self, request):
        try:
            roles = Role.objects.all()
            roles_serializer = RoleSerializer(roles, many=True)
            return Response(roles_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)