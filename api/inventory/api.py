from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Role, Category, Units, Coin, Product
from inventory.models import User
from .serializer import (UserSerializer, RoleSerializer, CategorySerializer, UnitSerializer, 
                         CoinSerializer, ProductSerializer, UserRegisterSerializer)
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.pagination import PageNumberPagination
from .filters import (UserFilter, RoleFilter, CategoryFilter, UnitFilter, CoinFilter, 
                      ProductFilter)
from django.contrib.auth import authenticate, login, logout

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication



class UserLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'message': 'Inicio de sesión exitoso'}, status=status.HTTP_200_OK)
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
            return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({"message": "User restored successfully"}, status=status.HTTP_200_OK)
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
            return Response({"message": "Role deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({"message": "Role restored successfully"}, status=status.HTTP_200_OK)
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
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({"message": "Categoría restaurada exitosamente"}, status=status.HTTP_200_OK)
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
            # Verifica si la unidad existe
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
            return Response({"message": "Unit deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({"message": "Units restored successfully"}, status=status.HTTP_200_OK)
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
            return Response({"message": "Coin deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({"message": "Coin restored successfully"}, status=status.HTTP_200_OK)
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
                return pagination.get_paginated_response({"products": serializer.data})
            
            serializer = ProductSerializer(products, many=True)
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
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "¡Producto registrado exitosamente!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            product = Product.objects.filter(pk=pk).first()
            if not product:
                return Response({
                    "mensaje": "El ID del producto no está registrado."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = ProductSerializer(product)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            # Si el valor es "null" como una cadena o un valor nulo real, manten el valor existente
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
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({"message": "Product restored successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "data": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": ["Se produjo un error interno"],
                    "errors": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)