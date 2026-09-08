from rest_framework.views import APIView
from django.db import connection
from master import globalparameters
from rest_framework.response import Response
import logging
from rest_framework import status
from django.db.models import F
from master.models import GlobalVdcMunicipality
import json
import ast
from django.conf import settings

DB_NAME = settings.DB_NAME

logger = logging.getLogger('django')

class VDCMunicipalityListAPIView(APIView):

   def get(self,request, *args):
      try:
         with connection.cursor() as cursor:
            query = """
            SELECT 
              gvm.name as municipality_name,
              gvm.reference_id as municipality_id,
              gd.reference_id as district_id
              FROM global_vdc_municipality gvm
            INNER JOIN global_district gd
            ON gvm.district_id = gd.id
            
            """
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result = [dict(zip(columns, row)) for row in rows]

            for item in result:
               item['referenceId'] = item.pop('municipality_id')
               item['name'] = item.pop('municipality_name')
               item['parentId'] = item.pop('district_id')

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





class AddressInfoAPIView(APIView):
    def get(self, request, *args, **kwargs):
        
        data = json.loads(json.dumps(ast.literal_eval(request.GET.get('jsonData'))))

        municipality_id = str(data['municipalityId']).strip() if 'municipalityId' else ''
        if not municipality_id:
            return Response({"error": "Municipality cannot be blank"},
                            status=status.HTTP_400_BAD_REQUEST)

        address = GlobalVdcMunicipality.objects.using(DB_NAME).filter(reference_id=municipality_id).annotate(
            districtId=F("district__reference_id"),
            provinceId=F("district__province__reference_id"),
        ).values("districtId", "provinceId").first()

        if address:
            response_msg = {
               globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_SUCCESS,
               globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
               "datas": address
            }
            return Response(response_msg, status=status.HTTP_200_OK)
        return Response({"error": "Municipality not found"}, status=status.HTTP_404_NOT_FOUND)
