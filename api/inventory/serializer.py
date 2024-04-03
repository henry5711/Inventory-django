from rest_framework import serializers
from django.contrib.auth.hashers import make_password 
from .models import User, Role

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

    def create(self, validated_data):
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