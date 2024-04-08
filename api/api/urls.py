from django.urls import path
from inventory.api import *
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
    
    path('category', CategoryIndexAPIView.as_view(), name='category-index'),
    path('category/create', CategoryStoreAPIView.as_view(), name='category-store'),
    path('category/<int:pk>', CategoryShowAPIView.as_view(), name='category-detail'),
    path('category/update/<int:pk>', CategoryUpdateAPIView.as_view(), name='category-update'),
    path('category/delete/<int:pk>', CategoryDeleteAPIView.as_view(), name='category-delete'),
    path('category/restore/<int:pk>', CategoryRestoreAPIView.as_view(), name='category-restore'),

    path('units', UnitIndexAPIView.as_view(), name='unit-index'),
    path('unit/create', UnitStoreAPIView.as_view(), name='unit-store'),
    path('unit/<int:pk>', UnitShowAPIView.as_view(), name='unit-detail'),
    path('unit/update/<int:pk>', UnitUpdateAPIView.as_view(), name='unit-update'),
    path('unit/delete/<int:pk>', UnitDeleteAPIView.as_view(), name='unit-delete'),
    path('unit/restore/<int:pk>', UnitRestoreAPIView.as_view(), name='unit-restore'),

    path('coins', CoinIndexAPIView.as_view(), name='coin-index'),
    path('coin/create', CoinStoreAPIView.as_view(), name='coin-store'),
    path('coin/<int:pk>', CoinShowAPIView.as_view(), name='coin-detail'),
    path('coin/update/<int:pk>', CoinUpdateAPIView.as_view(), name='coin-update'),
    path('coin/delete/<int:pk>', CoinDeleteAPIView.as_view(), name='coin-delete'),
    path('coin/restore/<int:pk>', CoinRestoreAPIView.as_view(), name='coin-restore'),
    
    path('products', ProductIndexAPIView.as_view(), name='product-index'),
    path('product/create', ProductStoreAPIView.as_view(), name='product-store'),
    path('product/<int:pk>', ProductShowAPIView.as_view(), name='product-detail'),
    path('product/update/<int:pk>', ProductUpdateAPIView.as_view(), name='product-update'),
    path('product/delete/<int:pk>', ProductDeleteAPIView.as_view(), name='product-delete'),
    path('product/restore/<int:pk>', ProductRestoreAPIView.as_view(), name='product-restore'),
    
    
]
