from rest_framework.views import APIView
from django.db import connection
from master import globalparameters
from rest_framework.response import Response
import logging
from rest_framework import status

logger = logging.getLogger('django')



class ProvinceListAPIView(APIView):

   
   def get(self,request, *args):
      try:
         with connection.cursor() as cursor:
            query = "SELECT * FROM global_province"
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result = [dict(zip(columns, row)) for row in rows]

            for item in result:
               item['referenceId'] = item.pop('reference_id')
               item['name'] = item.pop('name')

            success_msg = {
               globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_SUCCESS,
               globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION,
               "datas": result
            }

            return Response(success_msg, status=status.HTTP_200_OK)

      
      except ConnectionError as exc:
         logger.error(str(exc), exc_info=True)
         error_message = {
            globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CONNECTION_CODE,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
         }
         return Response(error_message.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      except Exception as exc:
         logger.error(str(exc), exc_info=True)
         error_message = {
            globalparameters.RESULT_CODE : globalparameters.RESULT_ERROR_CONNECTION_CODE,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
         }
         return Response(error_message.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


