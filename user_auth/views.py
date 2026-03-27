from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework.views import APIView
from master import globalparameters
from rest_framework import status
from rest_framework.response import Response
# from .authentication import TempSessionAuthenticationBackend
import json
from user_auth.serializers import UserSerializer
from django.http import JsonResponse
import logging
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import generate_uuid, UserSession
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User


logger = logging.getLogger('django')


class UserCreateAPIView(APIView):
   authentication_classes = ()
   permission_classes = (AllowAny,)

   def post(self,request,*args, **kwargs):
      serializer = UserSerializer(data=request.data,context={'reference_id': generate_uuid()})

      try:
         if serializer.is_valid():
            serializer.save()
            response_data = {
                globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
         else:
            response_data = {
                globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CODE,
                globalparameters.RESULT_DESCRIPTION : serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
      except Exception as e:
         logger.error(str(e),exc_info=True)
         response_data = {
                globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CODE,
                globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }   
         return Response(response_data,status=status.HTTP_500_INTERNAL_SERVER_ERROR)   



class LoginAPIView(APIView):
   authentication_classes = ()
   permission_classes = (AllowAny,)

   def post(self,request,*args, **kwargs):
      json_error = []
      try:

         if 'payload' in request.data:
            decrypted_payload = globalparameters.decrypt_payload(request.data['payload'])
            if decrypted_payload:
                try:
                    payload_data = json.loads(decrypted_payload)
                    username = str(payload_data.get('username', '')).strip()
                    password = str(payload_data.get('password', '')).strip()
                except Exception as e:
                    logger.error(f"Failed to parse decrypted payload: {str(e)}", exc_info=True)
                    username = ''
                    password = ''
            else:
                # If decryption failed, fall back to checking for raw username/password
                username = str(request.data.get('username', '')).strip()
                password = str(request.data.get('password', '')).strip()
         else:
            username = str(request.data['username']).strip() if 'username' in request.data else ''
            password = str(request.data['password']).strip() if 'password' in request.data else ''
         
         user = authenticate(username=username, password=password)
         if not user:
            json_error.append("Invalid Credentials")
         if json_error:
            logger.error(json_error,exc_info=True)
            json_data = {
               globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_INVALID_CREDENTIALS,
               globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_INVALID_CREDENTIALS
            }

            return JsonResponse(json_data, status=401)
         
         # token,_ = Token.objects.get_or_create(user=user)

         # temp_session_id = generate_uuid()

         # session,created = UserSession.objects.get_or_create(user=user)

         # if session:
         #    session.session_id = temp_session_id
         #    # session.expiry_date = datetime.now() + timedelta(minutes=15)
         #    session.save()
         #    user.temp_session_id = temp_session_id
         #    user.last_login = timezone.now()
         #    user.save()

            # request.session['auth_token'] = token.key
            # request.session['HTTP_AUTHORIZATION'] = temp_session_id

         refresh = RefreshToken.for_user(user)
         access = refresh.access_token
         
         json_data = {
            globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
            "username": user.first_name,
            "access_token": str(access),
            "refresh_token": str(refresh)
         }
         return JsonResponse(json_data, status=200)
         
         
      except Exception as e :
         logger.error(str(e), exc_info=True)
         error = {
            globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CODE,
            globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
         }

         return JsonResponse(error, status=500)



# class LogoutAPIView(APIView):

#    authentication_classes = (CookieJWTAuthentication,)
#    permission_classes = (TokenAuthentication,)
   
#    def post(self, request):
#       try:
#          # Authenticate user using the existing helper
#          # user = globalparameters.validation_for_authentication_parameters(request)
#          user = request.user
         
#          if isinstance(user, Response):
#                return user

#          if user and user.is_authenticated:
#                user.temp_session_id = None
#                user.save()
#                UserSession.objects.filter(user=user).delete()
#                logout(request)

#                response_data = {
#                   globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
#                   globalparameters.RESULT_DESCRIPTION: "Logout successful"
#                }

#                return JsonResponse(response_data, status=200)
#          else:
#                response_data = {
#                   globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
#                   globalparameters.RESULT_DESCRIPTION: "User not authenticated"
#                }
#                return JsonResponse(response_data, status=401)

#       except Exception as e:
#          logger.error(str(e), exc_info=True)
#          response_data = {
#                globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
#                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
#          }
#          return JsonResponse(response_data, status=500)

        
        


class LogoutAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"message": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST)

class UserListAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # users = User.objects.filter(is_active=True)
        users = User.objects.filter(is_superuser=False)
        serializer = UserSerializer(users, many=True)
        response_data = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
            "data": serializer.data,
            "datas": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserDetailAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, username, *args, **kwargs):
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)


class UserUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, username, *args, **kwargs):
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                    "message": "User updated successfully"
                }, status=status.HTTP_200_OK)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                "description": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)


class UserDeleteAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        if not username:
             return Response({"message": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            user.is_active = False
            user.save()
            return Response(
                {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                    "message": "User deleted successfully"
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND)