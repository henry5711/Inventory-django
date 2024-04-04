from rest_framework import serializers
from django.contrib.auth.hashers import make_password 
from .models import User, Role
from rest_framework_simplejwt.tokens import RefreshToken


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 
                  'name', 
                  'description', 
                  'created_at',
                  'updated_at',
                  'deleted_at',  ]

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe ser alfanumérica.")
        return value

    def create(self, validated_data):
        # Obtener el rol predeterminado (por ejemplo, el rol con ID 1)
        default_role = Role.objects.get(id=3)
        # Asignar el rol predeterminado al usuario
        validated_data['role'] = default_role
        validated_data['password'] = make_password(validated_data['password']) 
        return super().create(validated_data)
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