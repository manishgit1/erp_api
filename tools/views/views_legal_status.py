from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tools.models import LegalStatus
from tools.serializers import LegalStatusSerializer
from django.conf import settings
from master import globalparameters
import logging

DB_NAME = settings.DB_NAME
logger = logging.getLogger('django')

class LegalStatusListAPIView(APIView):

    def get(self, request):
        try:
            legal_status = LegalStatus.objects.using(DB_NAME).filter(is_void=False)
            serializer = LegalStatusSerializer(legal_status, many=True, context={"db_name": DB_NAME})
            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": serializer.data
            }
            return Response(response_msg, status=status.HTTP_200_OK)

        except LegalStatus.DoesNotExist as exc:
            logger.error(str(exc), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND
            }
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)
