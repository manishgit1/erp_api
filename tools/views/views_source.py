from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tools.models import LeadSource
from tools.serializers import LeadSourceSerializer
from django.conf import settings
import logging
from master import globalparameters
from user_auth.models import generate_uuid

logger = logging.getLogger('django')

DB_NAME = settings.DB_NAME
class LeadSourceCreateAPIView(APIView):
 
    def post(self, request):
        try:
            
          serializer = LeadSourceSerializer(data=request.data, context={'db_name': DB_NAME})
          if serializer.is_valid():
              serializer.save(reference_id=generate_uuid())
              return Response(serializer.data, status=status.HTTP_200_OK)
          else:
              return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as exc:
           logger.error(str(exc), exc_info=True)
           error_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
               globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS
           }
           return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class LeadSourceListAPIView(APIView):
    def get(self, request):
        try:
          lead_sources = LeadSource.objects.filter(is_void=False)
          serializer = LeadSourceSerializer(lead_sources, many=True)
          response_msg = {
             globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
             globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
             "datas": serializer.data
          }
          return Response(response_msg, status=status.HTTP_200_OK)
        except LeadSource.DoesNotExist as exc:
           logger.error(str(exc), exc_info=True)
           error_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
               globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND
           }
           return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
           logger.error(str(exc), exc_info=True)
           error_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
               globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS
           }
           return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
