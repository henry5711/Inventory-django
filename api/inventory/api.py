from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from inventory.models import User
from .serializer import *
from django.http import request
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.pagination import PageNumberPagination
from .filters import *
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.middleware.csrf import get_token
from django.middleware.csrf import rotate_token
from django.db.models import F
from rest_framework.exceptions import ValidationError
from django.urls import reverse
from django.shortcuts import redirect
from django.templatetags.static import static
from django.http import Http404
from django.conf import settings
from datetime import date

class WelcomeAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:

            return redirect('inventory-index')
        
        welcome_message = "¡Bienvenido! Por favor, inicia sesión o regístrate."
        
        login_url = reverse('login')
        
        welcome_message += f" Haz click aquí {login_url} para iniciar sesión."

        return Response(welcome_message)

class UserLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            rotate_token(request)
            csrf_token = request.META.get("CSRF_COOKIE")
            response = Response({'message': 'Inicio de sesión exitoso', 'csrf_token': csrf_token}, status=status.HTTP_200_OK)
            response.set_cookie('csrftoken', csrf_token)
            return response
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserLogoutAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'message': 'Cierre de sesión exitoso'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No hay ninguna sesión activa'}, status=status.HTTP_400_BAD_REQUEST)


class UserRegistration(APIView):
    def post(self, request):
        data = request.data.copy()
        data['role_id'] = 3  

        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "¡Has sido registrado exitosamente!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pag'


class UserIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()  
                return Response({"message": "¡Has sido registrado exitosamente!"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "error": "Se produjo un error interno",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:

            user = User.objects.filter(pk=pk).first()
            if not user:
                return Response({
                    "mensaje": "El ID de usuario no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = UserSerializer(user)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class UserUpdateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:

            user = User.objects.filter(pk=pk).first()
            if not user:
                return Response({
                    "message": "El ID de usuario no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)
            
            data = request.data
            
            for field, value in data.items():
                if value != 'null' and hasattr(user, field):
                    setattr(user, field, value)
            
            user.save()
            
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class UserDeleteAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            user = get_object_or_404(User, pk=pk)
            user.delete()
            return Response({"message": "¡Usuario eliminado exitosamente!"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRestoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user = get_object_or_404(User, pk=pk, deleted_at__isnull=False)
            user.deleted_at = None
            user.save()
            return Response({"message": "¡Usuario restaurada exitosamente!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            roles = Role.objects.all()
            
            role_filter = RoleFilter(request.query_params, queryset=roles)
            filtered_role = role_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_roles = pagination.paginate_queryset(filtered_role, request)
                serializer = RoleSerializer(paginated_roles, many=True)
                return pagination.get_paginated_response({"roles": serializer.data})
            
            serializer = RoleSerializer(filtered_role, many=True)
            return Response({"roles": serializer.data})
        
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
class RoleStoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = RoleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "¡Rol registrado exitosamente!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:

            role = Role.objects.filter(pk=pk).first()
            if not role:
                return Response({
                    "mensaje": "El ID del rol no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)


            serializer = RoleSerializer(role)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleUpdateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            role = Role.objects.get(pk=pk) 
            data = request.data
            
            for field, value in data.items():
                if value != 'null' and hasattr(role, field):
                    setattr(role, field, value)
            
            role.save()
            
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        except Role.DoesNotExist:
            return Response({
                "data": {
                    "code": status.HTTP_404_NOT_FOUND,
                    "errors": "El ID proporcionado no corresponde a ningún registro"
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RoleDeleteAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            role = get_object_or_404(Role, pk=pk)
            role.delete()
            return Response({"message": "¡Rol restaurada exitosamente!"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleRestoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            role = get_object_or_404(Role, pk=pk, deleted_at__isnull=False)
            role.deleted_at = None
            role.save()
            return Response({"message": "¡Categoría restaurada exitosamente!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            categories = Category.objects.all()

            if request.query_params:
                category_filter = CategoryFilter(request.query_params, queryset=categories)
                categories = category_filter.qs
            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_categories = pagination.paginate_queryset(categories, request)
                serializer = CategorySerializer(paginated_categories, many=True)
                return pagination.get_paginated_response({"categories": serializer.data})
            
            serializer = CategorySerializer(categories, many=True)
            return Response({"categories": serializer.data})
        
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
class CategoryStoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "¡Categoría registrada exitosamente!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:

            category = Category.objects.filter(pk=pk).first()
            if not category:
                return Response({
                    "mensaje": "El ID de la categoría no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)


            serializer = CategorySerializer(category)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryUpdateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:

            try:
                category = Category.objects.get(pk=pk)
            except Category.DoesNotExist:
                return Response({"message": "El ID de categoría no está registrado"}, status=status.HTTP_404_NOT_FOUND)
            
            data = request.data
            
            for field, value in data.items():
                if value != 'null' and hasattr(category, field):
                    setattr(category, field, value)
            
            category.save()
            
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CategoryDeleteAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            category = get_object_or_404(Category, pk=pk)
            category.delete()
            return Response({"message": "¡Categoría eliminada exitosamente!"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryRestoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            category = get_object_or_404(Category, pk=pk, deleted_at__isnull=False)
            category.deleted_at = None
            category.save()
            return Response({"message": "¡Categoría restaurada exitosamente!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UnitIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            units = Units.objects.all()

            if request.query_params:
                unit_filter = UnitFilter(request.query_params, queryset=units)
                units = unit_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination() 
                paginated_units = pagination.paginate_queryset(units, request)
                serializer = UnitSerializer(paginated_units, many=True)
                return pagination.get_paginated_response({"units": serializer.data})
            
            serializer = UnitSerializer(units, many=True)
            return Response({"units": serializer.data})
        
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UnitStoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = UnitSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "¡Unidad de medida registrada exitosamente!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnitShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:

            unit = Units.objects.filter(pk=pk).first()
            if not unit:
                return Response({
                    "mensaje": "El ID de la unidad no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)


            serializer = UnitSerializer(unit)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UnitUpdateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:

            if not Units.objects.filter(pk=pk).exists():
                return Response({
                    "message": "El ID no está registrado"
                }, status=status.HTTP_404_NOT_FOUND)
            
            unit = get_object_or_404(Units, pk=pk)
            
            data = request.data
            
            for field, value in data.items():
                if value != 'null' and hasattr(unit, field):
                    setattr(unit, field, value)
            
            unit.save()
            
            serializer = UnitSerializer(unit)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UnitDeleteAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            unit = get_object_or_404(Units, pk=pk)
            unit.delete()
            return Response({"message": "¡Unidad de medida eliminada exitosamente!"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UnitRestoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            unit = get_object_or_404(Units, pk=pk, deleted_at__isnull=False)
            unit.deleted_at = None
            unit.save()
            return Response({"message": "¡Unidad de medida restaurada exitosamente!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CoinIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            coins = Coin.objects.all()

            if request.query_params:
                coin_filter = CoinFilter(request.query_params, queryset=coins)
                coins = coin_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_coins = pagination.paginate_queryset(coins, request)
                serializer = CoinSerializer(paginated_coins, many=True)
                return pagination.get_paginated_response({"coins": serializer.data})
            
            serializer = CoinSerializer(coins, many=True)
            return Response({"coins": serializer.data})
        
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CoinStoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = CoinSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "¡Moneda registrada exitosamente!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CoinShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            coin = Coin.objects.filter(pk=pk).first()
            if not coin:
                return Response({
                    "mensaje": "El ID de la moneda no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)


            serializer = CoinSerializer(coin)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CoinUpdateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            coin = get_object_or_404(Coin, pk=pk)
        except Coin.DoesNotExist:
            return Response({
                "data": {
                    "code": status.HTTP_404_NOT_FOUND,
                    "title": ["El ID no está registrado"],
                    "errors": "El ID proporcionado no existe."
                }
            }, status=status.HTTP_404_NOT_FOUND)
            
        data = request.data
        
        for field, value in data.items():
            if value != 'null' and hasattr(coin, field):
                setattr(coin, field, value)
        
        coin.save()
        
        serializer = CoinSerializer(coin)
        return Response(serializer.data)

class CoinDeleteAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            coin = get_object_or_404(Coin, pk=pk)
            coin.delete()
            return Response({"message": "¡Moneda eliminada exitosamente!"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CoinRestoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            coin = get_object_or_404(Coin, pk=pk, deleted_at__isnull=False)
            coin.deleted_at = None
            coin.save()
            return Response({"message": "¡Moneda restaurada exitosamente!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            products = Product.objects.all()

            if request.query_params:
                product_filter = ProductFilter(request.query_params, queryset=products)
                products = product_filter.qs
                
            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_products = pagination.paginate_queryset(products, request)
                serializer = ProductSerializer(paginated_products, many=True)
            else:
                serializer = ProductSerializer(products, many=True)

            for product_data in serializer.data:
                image_name = product_data.pop('img', None)  
                if image_name:
                    image_url = settings.PRODUCT_IMAGE_BASE_URL + str(image_name)
                    product_data['image_url'] = image_url

            if 'pag' in request.query_params:
                return pagination.get_paginated_response({"products": serializer.data})
            else:
                return Response({"products": serializer.data})
        
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductStoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            category_id = request.data.get('category_id')
            units_id = request.data.get('units_id')

            if not (category_id and units_id):
                return Response({"error": "Los campos 'category_id' y 'units_id' son obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

            category_exists = Category.objects.filter(pk=category_id).exists()

            units_exists = Units.objects.filter(pk=units_id).exists()

            if not (category_exists or units_exists):
                raise ValidationError({"error": "Ninguno de los dos ID especificados existen."})

            if not category_exists:
                raise ValidationError({"error": "La categoría especificada no existe."})

            if not units_exists:
                raise ValidationError({"error": "Las unidades de medida especificadas no existen."})

            data = {
                'category_id': category_id,
                'units_id': units_id,
                'name': request.data.get('name'),
                'price': request.data.get('price'),
                'img': request.data.get('img')
            }

            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "¡Producto registrado exitosamente!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404("El producto no existe")

        serializer = ProductSerializer(product)
        product_data = serializer.data

        image_name = product_data.pop('img', None) 
        if image_name:
            image_url = settings.PRODUCT_IMAGE_BASE_URL + str(image_name)
            product_data['image_url'] = image_url
            return Response(product_data)
        else:
            return Response({
                "mensaje": "El campo 'img' no está presente en los datos del producto."
            }, status=status.HTTP_404_NOT_FOUND)

        
class ProductUpdateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
        except Product.DoesNotExist:
            return Response({
                "data": {
                    "code": status.HTTP_404_NOT_FOUND,
                    "title": ["El ID no está registrado"],
                    "errors": "El ID proporcionado no existe."
                }
            }, status=status.HTTP_404_NOT_FOUND)
            
        data = request.data
        
        for field, value in data.items():
           
            if value == "null" or value is None:
                continue
            if hasattr(product, field):
                setattr(product, field, value)
        
        product.save()
        
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
class ProductDeleteAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
            product.delete()
            return Response({"message": "¡Producto eliminado exitosamente!"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductRestoreAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk, deleted_at__isnull=False)
            product.deleted_at = None
            product.save()
            return Response({"message": "¡Producto restaurado exitosamente!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class InventoryIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            inventories = Inventory.objects.all()

            if request.query_params:
                inventory_filter = InventoryFilter(request.query_params, queryset=inventories)
                inventories = inventory_filter.qs
                
            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_inventories = pagination.paginate_queryset(inventories, request)
                serializer = InventorySerializer(paginated_inventories, many=True)
            else:
                serializer = InventorySerializer(inventories, many=True)

            for inventory_data in serializer.data:
                product_data = inventory_data.get('product')
                if product_data and 'img' in product_data:

                    product_data['image_url'] = settings.PRODUCT_IMAGE_BASE_URL + str(product_data['img'])

                    product_data.pop('img')

            if 'pag' in request.query_params:
                return pagination.get_paginated_response({"inventories": serializer.data})
            else:
                return Response({"inventories": serializer.data})
        
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class InventoryAddInputAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not Product.objects.filter(id=product_id).exists():
            return Response({"message": "Este producto no existe."}, status=status.HTTP_404_NOT_FOUND)

        try:
            inventory = Inventory.objects.get(product_id=product_id)
            inventory.quantity += quantity

            product_price = inventory.product.price
            inventory.total_price = product_price * inventory.quantity

            if inventory.quantity >= inventory.min_quantity:
                warning_message = ""
            else:
                warning_message = f"¡La cantidad del producto {inventory.product.name} ha alcanzado o superado {inventory.min_quantity} unidades!"

            inventory.save()

            Input.objects.create(
                inventory=inventory,
                quantity=quantity
            )

            return Response({"message": "¡El inventario se actualizó exitosamente!", "Cantidad actual": inventory.quantity, }, status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:
            product = Product.objects.get(id=product_id)
            inventory = Inventory.objects.create(product=product, quantity=quantity, min_quantity=5)

            product_price = inventory.product.price
            inventory.total_price = product_price * inventory.quantity

            inventory.save()

            Input.objects.create(
                inventory=inventory,
                quantity=quantity
            )

            return Response({"message": f"¡Producto agregado exitosamente! Cantidad mínima establecida por default es 5, actualizala.", "Cantidad actual": inventory.quantity, "Precio total": inventory.total_price}, status=status.HTTP_201_CREATED)

class InventoryAddMinQuantityInputAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        min_quantity = request.data.get('min_quantity')

        try:
            inventory = Inventory.objects.get(product_id=product_id)
            inventory.min_quantity = min_quantity
            inventory.save()

            return Response({"message": f"¡Se ha actualizado el min_quantity del inventario del producto con ID {product_id} exitosamente!", "Nuevo min_quantity": inventory.min_quantity}, status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:

            inventory = Inventory.objects.create(product_id=product_id, quantity=0, min_quantity=min_quantity)
            return Response({"message": f"¡Se ha creado un nuevo inventario para el producto con ID {product_id}!", "Nuevo min_quantity": inventory.min_quantity}, status=status.HTTP_201_CREATED)
        
class InventoryUpdateMinQuantityAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, inventory_id):
        min_quantity = request.data.get('min_quantity')

        try:
            inventory = Inventory.objects.get(id=inventory_id)

            inventory.min_quantity = min_quantity
            inventory.save()

            return Response({"message": f"¡Se ha actualizado el min_quantity del inventario con ID {inventory_id} exitosamente!", "Nuevo min_quantity": inventory.min_quantity}, status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:
            return Response({"message": f"El inventario con ID {inventory_id} no existe"}, status=status.HTTP_404_NOT_FOUND)



class InventorySubOutputAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        try:
            # Verificar si ya existe un usuario con el documento proporcionado
            document = request.data.get('document')
            existing_user = User.objects.filter(document=document).exists()

            if existing_user:
                # Si el usuario ya existe, obtener la instancia del usuario existente
                current_user = User.objects.get(document=document)
            else:
                # Si el usuario no existe, crear uno nuevo
                user_data = {
                    "username": document,  # Utiliza el documento como nombre de usuario
                    "email": request.data.get('email'),
                    "document": document,
                    "address": request.data.get('address'),
                    "phone_number": request.data.get('phone_number'),
                    "name": request.data.get('name'),
                    "last_name": request.data.get('last_name')
                }
                user_serializer = UserRegisterClientSerializer(data=user_data)
                if user_serializer.is_valid():
                    current_user = user_serializer.save()
                else:
                    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            inventory = Inventory.objects.get(product_id=product_id)
            if inventory.quantity < quantity:
                return Response({"message": "La cantidad solicitada es mayor que la cantidad en inventario", "cantidad existente": inventory.quantity}, status=status.HTTP_400_BAD_REQUEST)

            inventory.quantity -= quantity
            inventory.total_price = inventory.product.price * inventory.quantity
            inventory.save()  

            Output.objects.create(
                inventory=inventory,
                quantity=quantity
            )

            bill_detail = Detail.objects.create(
                inventory=inventory,
                quantity=quantity,
                price_unit=inventory.product.price,
                subtotal=inventory.product.price * quantity
            )

            bill = Bill.objects.create(
                user=current_user,
                detail=bill_detail,
                total_price=bill_detail.subtotal,
                date=timezone.now()  # Asegurarse de establecer la fecha adecuadamente
            )

            if inventory.quantity <= inventory.min_quantity:
                warning_message = f"¡La cantidad del producto {inventory.product.name} ha llegado al mínimo de {inventory.min_quantity}!"
            else:
                warning_message = ""

            response_data = {"message": "Inventario actualizado satisfactoriamente!", "cantidad actual": inventory.quantity}
            if warning_message:
                response_data["Advertencia"] = warning_message

            return Response(response_data, status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:
            return Response({"message": f"El producto con ID {product_id} no existe"}, status=status.HTTP_404_NOT_FOUND)


class InventoryShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:

            inventory = Inventory.objects.filter(pk=pk).first()
            
            if not inventory:
                return Response({
                    "mensaje": "El ID del inventario no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)

            inventory_serializer = InventorySerializer(inventory)

            return Response(inventory_serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class InputIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            inputs = Input.objects.all()

            if request.query_params:
                input_filter = InputFilter(request.query_params, queryset=inputs)
                inputs = input_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_inputs = pagination.paginate_queryset(inputs, request)
                serializer = InputSerializer(paginated_inputs, many=True)
                return pagination.get_paginated_response({"inputs": serializer.data})

            serializer = InputSerializer(inputs, many=True)
            return Response({"inputs": serializer.data})

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InputShowAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            input_obj = Input.objects.filter(pk=pk).first()
            if not input_obj:
                return Response({
                    "mensaje": "El ID de la entrada no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = InputSerializer(input_obj)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class OutputIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            outputs = Output.objects.all()

            if request.query_params:
                output_filter = OutputFilter(request.query_params, queryset=outputs)
                outputs = output_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_outputs = pagination.paginate_queryset(outputs, request)
                serializer = OutputSerializer(paginated_outputs, many=True)
                return pagination.get_paginated_response({"outputs": serializer.data})

            serializer = OutputSerializer(outputs, many=True)
            return Response({"outputs": serializer.data})

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OutputShowAPIView(APIView):

    def get(self, request, pk):
        try:
            Output_obj = Output.objects.filter(pk=pk).first()
            if not Output_obj:
                return Response({
                    "mensaje": "El ID de la salida no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = OutputSerializer(Output_obj)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class DetailIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            details = Detail.objects.all()

            if request.query_params:
                Detail_filter = DetailFilter(request.query_params, queryset=details)
                details = Detail_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_details = pagination.paginate_queryset(details, request)
                serializer = DetailSerializer(paginated_details, many=True)
                return pagination.get_paginated_response({"details": serializer.data})

            serializer = DetailSerializer(details, many=True)
            return Response({"details": serializer.data})

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetailShowAPIView(APIView):

    def get(self, request, pk):
        try:
            Detail_obj = Detail.objects.filter(pk=pk).first()
            if not Detail_obj:
                return Response({
                    "mensaje": "El ID de la salida no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = DetailSerializer(Detail_obj)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BillIndexAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            bills = Bill.objects.all()

            if request.query_params:
                bill_filter = BillFilter(request.query_params, queryset=bills)
                bills = bill_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_bills = pagination.paginate_queryset(bills, request)
                serializer = BillSerializer(paginated_bills, many=True)
                return pagination.get_paginated_response({"bills": serializer.data})

            serializer = BillSerializer(bills, many=True)
            return Response({"bills": serializer.data})

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BillShowAPIView(APIView):

    def get(self, request, pk):
        try:
            Bill_obj = Bill.objects.filter(pk=pk).first()
            if not Bill_obj:
                return Response({
                    "mensaje": "El ID de la salida no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = BillSerializer(Bill_obj)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        