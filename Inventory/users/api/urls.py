from django.urls import path
from users.api.api import (
    UserIndexAPIView,
    UserStoreAPIView,
    UserShowAPIView,
    UserUpdateAPIView,
    UserDeleteAPIView,
    UserRestoreAPIView,
    RoleIndexAPIView,
)

urlpatterns = [
    path('', UserIndexAPIView.as_view(), name='user_list'),
    path('create/', UserStoreAPIView.as_view(), name='user_create'),
    path('show/<int:pk>/', UserShowAPIView.as_view(), name='user_show'),
    path('update/<int:pk>/', UserUpdateAPIView.as_view(), name='user_update'),
    path('delete/<int:pk>/', UserDeleteAPIView.as_view(), name='user_delete'),
    path('restore/<int:pk>/', UserRestoreAPIView.as_view(), name='user_restore'),
    path('roles/', RoleIndexAPIView.as_view(), name='role_index'),
]