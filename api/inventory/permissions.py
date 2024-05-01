from rest_framework.permissions import BasePermission

class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role:
            permissions = request.user.role.rolepermission_set.all()
            for permission in permissions:
                if permission.permission.codename in view.required_permissions:
                    return True
        return False