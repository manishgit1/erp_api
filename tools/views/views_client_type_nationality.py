from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tools.models import Nationality
from tools.serializers import NationalitySerializer
from django.db import transaction
from django.conf import settings
from master import globalparameters
import logging
import datetime
from master.models import generate_uuid

DB_NAME = settings.DB_NAME
logger = logging.getLogger('django')

class NationalityCreateAPIView(APIView):

    @transaction.atomic
    def post(self, request):
       try:
            
            user =globalparameters.validation_for_authentication_parameters(request)
            serializer = NationalitySerializer(data=request.data, context={"db_name": DB_NAME})
            if serializer.is_valid():
                serializer.save(reference_id=generate_uuid(),created_at=datetime.datetime.now(),created_by=user)
                response_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS
                }
                return Response(response_msg, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       except Exception as exc:
           logger.error(str(exc), exc_info=True)
           response_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
               globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
           }
           return Response(response_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NationalityListAPIView(APIView):
    
    def get(self, request):
        try:
            nationality = Nationality.objects.using(DB_NAME).filter(is_void=False)
            serializer = NationalitySerializer(nationality, many=True, context={"db_name": DB_NAME})
            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": serializer.data
            }
            return Response(response_msg, status=status.HTTP_200_OK)
        
        except Nationality.DoesNotExist as exc:
            logger.error(str(exc), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND
            }
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)
