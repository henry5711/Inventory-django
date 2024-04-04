from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User, Role
from .serializer import UserSerializer, RoleSerializer
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.pagination import PageNumberPagination
from .filters import UserFilter 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User 
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth import get_user_model

class UserLoginAPIView(APIView):
    authentication_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is not None and user.check_password(password):
            if user.is_active:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'message': 'Inicio de sesión exitoso', 'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Este usuario está inactivo'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"detail": "Nombre de usuario o contraseña inválidos."}, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'message': 'Sesión cerrada exitosamente'}, status=status.HTTP_200_OK)
    
class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pag'


class UserIndexAPIView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()

            user_filter = UserFilter(request.query_params, queryset=users)
            filtered_users = user_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_users = pagination.paginate_queryset(filtered_users, request)
                serializer = UserSerializer(paginated_users, many=True)
                return pagination.get_paginated_response({"users": serializer.data})
            
            serializer = UserSerializer(filtered_users, many=True)
            return Response({"users": serializer.data})
        
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
class UserStoreAPIView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserShowAPIView(APIView):
    def get(self, request, pk):
        try:
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            user = get_object_or_404(User, pk=pk)
            new_role_id = request.data.get('role_id')
            if new_role_id is not None:
                if not Role.objects.filter(id=new_role_id).exists():
                    return Response({"error": f"El role con ID {new_role_id} no existe."}, status=status.HTTP_400_BAD_REQUEST)
                user.role_id = new_role_id
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            user = get_object_or_404(User, pk=pk)
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRestoreAPIView(APIView):
    def get(self, request, pk):
        try:
            user = get_object_or_404(User, pk=pk, deleted_at__isnull=False)
            user.deleted_at = None
            user.save()
            return Response({"message": "User restored successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class RoleIndexAPIView(APIView):
    def get(self, request):
        try:
            roles = Role.objects.all()
            
            role_filter = UserFilter(request.query_params, queryset=roles)
            filtered_role = role_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_roles = pagination.paginate_queryset(filtered_role, request)
                serializer = RoleSerializer(paginated_roles, many=True)
                return pagination.get_paginated_response({"roles": serializer.data})
            
            serializer = RoleSerializer(filtered_role, many=True)
            return Response({"roles": serializer.data})
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RoleStoreAPIView(APIView):
    def post(self, request):
        try:
            serializer = RoleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            role = get_object_or_404(Role, pk=pk)
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            role = get_object_or_404(Role, pk=pk)
            data = {key: value for key, value in request.data.items() if key in RoleSerializer.Meta.fields}
            serializer = RoleSerializer(role, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            role = get_object_or_404(Role, pk=pk)
            role.delete()
            return Response({"message": "Role deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleRestoreAPIView(APIView):
    def get(self, request, pk):
        try:
            role = get_object_or_404(Role, pk=pk, deleted_at__isnull=False)
            role.deleted_at = None
            role.save()
            return Response({"message": "Role restored successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)