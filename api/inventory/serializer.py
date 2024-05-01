from rest_framework import serializers
from django.contrib.auth.hashers import make_password 
from .models import *
from inventory.models import User
import os
  
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 
                  'name', 
                  'description', 
                  'created_at',
                  'updated_at',
                  'deleted_at',  ]
    def validate_name(self, value):

        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("Ya existe un rol con este nombre.")
        return value

    def create(self, validated_data):

        return Role.objects.create(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True) 

    def validate_role_id(self, value):
        try:
            role = Role.objects.get(pk=value) 
        except Role.DoesNotExist:
            raise serializers.ValidationError("El ID de rol proporcionado no existe.") 
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe ser alfanumérica.")
        return value
    
    def create(self, validated_data):
        role_id = validated_data.pop('role_id')
        validated_data['username'] = validated_data['username'].lower()
        validated_data['password'] = make_password(validated_data['password']) 
        user = super().create(validated_data)
        role = Role.objects.get(pk=role_id)
        user.role = role
        user.save()
        return user
    
    class Meta:
        model = User
        fields = ['id', 
                  'username', 
                  'password',
                  'email', 
                  'name', 
                  'last_name', 
                  'role_id',
                  'image', 
                  'document', 
                  'address',
                  'phone_number',
                  'is_active',
                  'is_staff',
                  'created_at',
                  'updated_at',
                  'deleted_at',  
                  'role', ]
        extra_kwargs = {
            'password': {'write_only': True},  
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 
                  'password', 
                  'email', 
                  'name', 
                  'last_name', 
                  'document', 
                  'address',
                  'phone_number', ]

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe ser alfanumérica.")
        return value

    def create(self, validated_data):
        default_role = Role.objects.get(id=4)
        validated_data['role'] = default_role
        validated_data['username'] = validated_data['username'].lower()
        validated_data['password'] = make_password(validated_data['password']) 
        return super(UserRegisterSerializer, self).create(validated_data)
    
class UserRegisterClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 
                  'password', 
                  'email', 
                  'name', 
                  'last_name', 
                  'document', 
                  'address',
                  'phone_number', ]

    def create(self, validated_data):
        role_id = 3  # ID del rol que activará la creación de username y password con el documento
        default_role = Role.objects.get(id=role_id)
        validated_data['role'] = default_role
        
        # Si el rol es 3, username y password serán el documento
        if default_role.id == role_id:
            validated_data['username'] = validated_data['document']
            validated_data['password'] = make_password(validated_data['document'])
        
        return super(UserRegisterClientSerializer, self).create(validated_data)
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 
                  'name', 
                  'description', 
                  'created_at',
                  'updated_at',
                  'deleted_at',  ]

    def validate_name(self, value):
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("Ya existe una categoría con este nombre.")
        return value

    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    
class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Units
        fields = ['id', 
                  'name', 
                  'description', 
                  'abbreviation', 
                  'created_at',
                  'updated_at',
                  'deleted_at']

    def validate_name(self, value):
        if Units.objects.filter(name=value).exists():
            raise serializers.ValidationError("Ya existe una unidad con este nombre.")
        return value

    def create(self, validated_data):
        return Units.objects.create(**validated_data)
    
class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ['id', 
                  'name', 
                  'description', 
                  'symbol', 
                  'abbreviation', 
                  'created_at', 
                  'updated_at', 
                  'deleted_at']

    def validate_name(self, value):
        if Coin.objects.filter(name=value).exists():
            raise serializers.ValidationError("Ya existe una moneda con este nombre.")
        return value

    def create(self, validated_data):
        return Coin.objects.create(**validated_data)
 
IMAGE_DOMAIN = os.environ.get('IMAGE_DOMAIN', 'https://dominio-por-defecto.com')

class ProductSerializer(serializers.ModelSerializer):

    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    units_id = serializers.PrimaryKeyRelatedField(queryset=Units.objects.all(), write_only=True)

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        units_id = validated_data.pop('units_id', None)

        product = Product.objects.create(**validated_data)

        if category_id:
            product.category = category_id
        if units_id:
            product.units = units_id

        product.save()
        return product

    class Meta:
        model = Product
        fields = ['id', 
                  'name', 
                  'description', 
                  'price', 
                  'units_id',  
                  'category_id',  
                  'img', 
                  'created_at',
                  'updated_at',
                  'deleted_at',  
                  ]
        
class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ['id',
                  'product_id',
                  'quantity',  
                  'min_quantity',
                  'created_at', 
                  'updated_at',
                  'deleted_at',
                  'product']

    def create(self, validated_data):
        inventory_instance = Inventory.objects.create(**validated_data)
        input_data = {
            'inventory_id': inventory_instance.id,
            'quantity': inventory_instance.quantity
        }
        input_instance = Input.objects.create(**input_data)

        return inventory_instance


class InputSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    class Meta:
        model = Input
        fields = ['id',
                  'inventory_id', 
                  'quantity',  
                  'created_at', 
                  'updated_at',
                  'deleted_at',
                  'inventory']

    def create(self, validated_data):
        return Input.objects.create(**validated_data)
    
class OutputSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = Output
        fields = ['id',
                  'inventory_id', 
                  'quantity',  
                  'created_at', 
                  'updated_at',
                  'deleted_at',
                  'inventory']

    def create(self, validated_data):
        return Output.objects.create(**validated_data)

        
class DetailSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = Detail
        fields =  ['id',
                  'inventory_id', 
                  'quantity',  
                  'price_unit',  
                  'subtotal',  
                  'created_at', 
                  'updated_at',
                  'deleted_at',
                  'inventory']
        
class BillSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    detail = DetailSerializer(read_only=True)
    user_id = UserSerializer(write_only=True) 
    detail_id = DetailSerializer(write_only=True) 

    class Meta:
        model = Bill
        fields = ['id',
                  'date', 
                  'user_id',  
                  'detail_id',
                  'total_price',    
                  'created_at', 
                  'updated_at',
                  'deleted_at',
                  'user',
                  'detail']