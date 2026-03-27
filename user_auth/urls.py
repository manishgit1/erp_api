from django.urls import path
from .views import (
    UserCreateAPIView, 
    LoginAPIView, 
    LogoutAPIView, 
    UserListAPIView, 
    UserDetailAPIView, 
    UserUpdateAPIView, 
    UserDeleteAPIView
)
from .views_role import (
    RoleCreateAPIView,
    RoleListAPIView,
    RoleGetByIdAPIView,
    RoleEditAPIView,
    RoleDeleteAPIView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
       
       path('user/create', UserCreateAPIView.as_view(), name='user-create'),
       path('user/list', UserListAPIView.as_view(), name='user-list'),
       path('user/detail/<str:username>', UserDetailAPIView.as_view(), name='user-detail'),
       path('user/update/<str:username>', UserUpdateAPIView.as_view(), name='user-update'),
       path('user/delete', UserDeleteAPIView.as_view(), name='user-delete'),

       path('user/register', UserCreateAPIView.as_view(), name='user-registration'),
       path('user/login', LoginAPIView.as_view(), name='user-login'),
       path('user/logout', LogoutAPIView.as_view(), name='user-logout'),

       # Role CRUD
       path('role/create', RoleCreateAPIView.as_view(), name='role-create'),
       path('role/list', RoleListAPIView.as_view(), name='role-list'),
       path('role/findById/<int:pk>', RoleGetByIdAPIView.as_view(), name='role-find-by-id'),
       path('role/edit/<int:pk>', RoleEditAPIView.as_view(), name='role-edit'),
       path('role/delete/<int:pk>', RoleDeleteAPIView.as_view(), name='role-delete'),

]