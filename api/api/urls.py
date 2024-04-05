from django.urls import path
from inventory.api import (UserIndexAPIView, UserStoreAPIView, UserShowAPIView, UserUpdateAPIView, UserDeleteAPIView, UserRestoreAPIView,
                           RoleIndexAPIView, RoleStoreAPIView, RoleShowAPIView, RoleUpdateAPIView, RoleDeleteAPIView, RoleRestoreAPIView, 
                            UserLogoutAPIView, UserLoginAPIView, UserRegistration,
                           )
urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('register/', UserRegistration.as_view(), name='user-registration'),
    path('users', UserIndexAPIView.as_view(), name='user-list'),
    path('user/create', UserStoreAPIView.as_view(), name='user-create'),
    path('user/<int:pk>', UserShowAPIView.as_view(), name='user-detail'),
    path('user/update/<int:pk>', UserUpdateAPIView.as_view(), name='user-update'),
    path('user/delete/<int:pk>', UserDeleteAPIView.as_view(), name='user-delete'),
    path('user/restore/<int:pk>', UserRestoreAPIView.as_view(), name='user-restore'),
    path('roles', RoleIndexAPIView.as_view(), name='role-list'),
    path('role/create', RoleStoreAPIView.as_view(), name='role-create'),
    path('role/<int:pk>', RoleShowAPIView.as_view(), name='role-detail'),
    path('role/update/<int:pk>', RoleUpdateAPIView.as_view(), name='role-update'),
    path('role/delete/<int:pk>', RoleDeleteAPIView.as_view(), name='role-delete'),
    path('role/restore/<int:pk>', RoleRestoreAPIView.as_view(), name='role-restore'),
]
