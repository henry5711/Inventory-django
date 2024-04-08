from rest_framework import serializers
from django.contrib.auth.hashers import make_password 
from .models import Role, Category, Units, Coin, Product
from inventory.models import User


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

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe ser alfanumérica.")
        return value
    
    def create(self, validated_data):
        role_id = validated_data.pop('role_id')
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
        default_role = Role.objects.get(id=3)
        validated_data['role'] = default_role
        validated_data['password'] = make_password(validated_data['password']) 
        return super(UserRegisterSerializer, self).create(validated_data)
    
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
        fields = ['id', 'name', 'description', 'symbol', 'abbreviation', 'created_at', 'updated_at', 'deleted_at']

    def validate_name(self, value):
        if Coin.objects.filter(name=value).exists():
            raise serializers.ValidationError("Ya existe una moneda con este nombre.")
        return value

    def create(self, validated_data):
        return Coin.objects.create(**validated_data)
    
class ProductSerializer(serializers.ModelSerializer):
  

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    class Meta:
        model = Product
        fields = ['id', 
                  'name', 
                  'description', 
                  'price', 
                  'units', 
                  'category', 
                  'img', 
                  'created_at',
                  'updated_at',
                  'deleted_at',  
                  ]