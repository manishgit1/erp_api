from django.urls import path
from .views import UserRegisterAPIView, LoginAPIView, LogoutAPIView

urlpatterns = [
       
       path('user/register', UserRegisterAPIView.as_view(), name='user-registration'),
       path('user/login', LoginAPIView.as_view(), name='user-login'),
       path('user/logout', LogoutAPIView.as_view(), name='user-logout'),

]