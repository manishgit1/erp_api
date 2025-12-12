from rest_framework.views import APIView
from rest_framework import status
from tools.models import SystemDay
from django.conf import settings
from rest_framework.response import Response
import logging
from master import globalparameters

logger = logging.getLogger('django')
DB_NAME = settings.DB_NAME

class GetBusinessDateAPIView(APIView):
  
 def get(self,request,format=None):
   
   try:
     business_date = SystemDay.objects.using(DB_NAME).filter(is_open=True).first()
     json_data = {
       globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
       globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
       'business_date_ad': business_date.business_date_ad
     }

     return Response(json_data,status=status.HTTP_200_OK)
  
   except Exception as e:
     logger.error(str(e),exc_info=True)
     response_msg = {
       globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
       globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR,
     }

     return Response(response_msg,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      