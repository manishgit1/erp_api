from rest_framework.views import APIView
from django.db import connection
from master import globalparameters
from rest_framework.response import Response
import logging
from rest_framework import status

logger = logging.getLogger('django')

class DistrictListAPIView(APIView):

   def get(self,request, *args):
      try:
         with connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
                d.reference_id AS district_id,
                d.name AS district_name,
                p.reference_id AS province_id
            FROM global_district d
            INNER JOIN global_province p ON d.province_id = p.id
        """)
            # query = "SELECT gd.name 'districtName', gd.reference_id 'districtId', gp.reference_id 'provinceId' FROM global_district gd LEFT JOIN global_province gp ON gd.province_id = gp.id"
            # cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result = [dict(zip(columns, row)) for row in rows]

            for item in result:
               item['referenceId'] = item.pop('district_id')
               item['name'] = item.pop('district_name')
               item['parentId'] = item.pop('province_id')

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
