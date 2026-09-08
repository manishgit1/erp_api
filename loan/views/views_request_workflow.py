from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from loan.models import RequestWorkflow
from loan.serializers import RequestWorkflowSerializer
from master import globalparameters
import logging
from user_auth.models import generate_uuid

logger = logging.getLogger('django')

class RequestWorkflowListAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        workflows = RequestWorkflow.objects.all()
        serializer = RequestWorkflowSerializer(workflows, many=True)
        return Response({
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            "data": serializer.data,
            "datas": serializer.data
        }, status=status.HTTP_200_OK)


class RequestWorkflowCreateAPIView(APIView):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        workflow_steps = request.data.get('workflowSteps', [])
        if not workflow_steps:
             return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                "message": "workflowSteps list is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_items = []
        try:
            for step in workflow_steps:
                serializer = RequestWorkflowSerializer(data=step)
                if serializer.is_valid():
                    # We pass reference_id through context or explicitly set it
                    # But GenericIdEntity has a default generate_uuid() which might be enough
                    # However, UserRegisterAPIView uses generate_uuid() manually.
                    # Let's use the model's default if possible, or follow the pattern.
                    serializer.save(reference_id=generate_uuid())
                    created_items.append(serializer.data)
                else:
                    return Response({
                        globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                        "message": "Validation failed",
                        "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                "message": f"Successfully created {len(created_items)} workflow steps",
                "data": created_items
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                "message": globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
