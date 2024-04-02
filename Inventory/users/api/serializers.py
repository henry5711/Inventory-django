from rest_framework import serializers
from users.models import User, Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'deleted_at']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = RoleSerializer()  # Agrega este campo para serializar el rol

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'name', 'last_name', 'role', 'image', 'document', 'address', 'phone_number', 'is_active', 'is_staff', 'created_at', 'updated_at', 'deleted_at']
    
    def create(self, validated_data):
        role_data = validated_data.pop('role', None)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
            last_name=validated_data['last_name'],
            role=Role.objects.create(**role_data) if role_data else None,  # Crea el rol si existe
            image=validated_data.get('image', None),
            document=validated_data['document'],
            address=validated_data['address'],
            phone_number=validated_data['phone_number'],
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        role_data = validated_data.pop('role', None)
        if role_data:
            role_serializer = RoleSerializer(instance.role, data=role_data)
            if role_serializer.is_valid():
                role_serializer.save()
            else:
                raise serializers.ValidationError(role_serializer.errors)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.image = validated_data.get('image', instance.image)
        instance.document = validated_data.get('document', instance.document)
        instance.address = validated_data.get('address', instance.address)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
