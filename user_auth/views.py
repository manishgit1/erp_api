from django.shortcuts import render
from rest_framework.views import APIView
from master import globalparameters
from rest_framework import status
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
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import logout


logger = logging.getLogger('django')


class UserRegisterAPIView(APIView):
   def post(self,request,*args, **kwargs):
      serializer = UserSerializer(data=request.data,context={'reference_id': generate_uuid()})

      try:
         if serializer.is_valid():
            serializer.save()
            response_data = {
                globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS
            }

            return JsonResponse(response_data, status=200)
         else:
            response_data = {
                globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CODE,
                globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return JsonResponse(response_data, status=400)
            
      except Exception as e:
         logger.error(str(e),exc_info=True)
         response_data = {
                globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CODE,
                globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }   
         return JsonResponse(response_data,status=200)   



class LoginAPIView(APIView):
   authentication_classes = ()
   permission_classes = ()

   def post(self,request,*args, **kwargs):
      json_error = []
      try:
         username = request.data['username'] if 'username' in request.data else ''
         password = request.data['password'] if 'password' in request.data else ''
         
         user = authenticate(username=username, password=password)
         if not user:
            json_error.append("Invalid Credentials")
         if json_error:
            json_data = {
               globalparameters.RESULT_CODE : globalparameters.RESULT_DESCRIPTION_INVALID_CREDENTIALS,
               globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_CODE_INVALID_CREDENTIALS
            }

            return JsonResponse(json_data, status=401)
         
         # token,_ = Token.objects.get_or_create(user=user)

         temp_session_id = generate_uuid()

         session,created = UserSession.objects.get_or_create(user=user)

         if session:
            session.session_id = temp_session_id
            # session.expiry_date = datetime.now() + timedelta(minutes=15)
            session.save()
            user.temp_session_id = temp_session_id
            user.last_login = timezone.now()
            user.save()

            # request.session['auth_token'] = token.key
            # request.session['HTTP_AUTHORIZATION'] = temp_session_id
            
            json_data = {
               globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_SUCCESS,
               globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
               "temp_session_id": temp_session_id,
               "username": user.first_name
            }
            return JsonResponse(json_data, status=200)
         
         
      except Exception as e :
         logger.error(str(e), exc_info=True)
         error = {
            globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CODE,
            globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
         }

         return JsonResponse(error, status=500)



class LogoutAPIView(APIView):
    def get(self, request):
        
         user = globalparameters.validation_for_authentication_parameters(request)
         if user:
            logout(request)
            return JsonResponse({"message":"Logout success"}, status=200)
         else:
            return JsonResponse({"message":"User not logged in"}, status=400)

        
        


      