from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from datetime import datetime
import logging

from master import globalparameters
from user_auth.models import UserRole, generate_uuid
from user_auth.serializers import UserRoleSerializer

logger = logging.getLogger('django')

DB_NAME = settings.DB_NAME


class RoleCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            user = globalparameters.validation_for_authentication_parameters(request)

            serializer = UserRoleSerializer(data=request.data, context={'db_name': DB_NAME})
            serializer.is_valid(raise_exception=True)
            serializer.save(
                reference_id=generate_uuid(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=user,
                updated_by=user,
            )

            success_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
            }
            return Response(success_msg, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR,
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            roles = UserRole.objects.using(DB_NAME).all()
            serializer = UserRoleSerializer(roles, many=True, context={'db_name': DB_NAME})

            response = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                'datas': serializer.data,
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR,
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleGetByIdAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk, *args, **kwargs):
        try:
            role = UserRole.objects.using(DB_NAME).filter(id=pk).first()

            if not role:
                error_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND,
                }
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

            serializer = UserRoleSerializer(role, context={'db_name': DB_NAME})

            response = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                'datas': serializer.data,
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR,
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleEditAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pk, *args, **kwargs):
        try:
            user = globalparameters.validation_for_authentication_parameters(request)

            role = UserRole.objects.using(DB_NAME).filter(id=pk).first()

            if not role:
                error_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND,
                }
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

            serializer = UserRoleSerializer(
                instance=role,
                data=request.data,
                partial=True,
                context={'db_name': DB_NAME},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_at=datetime.now(), updated_by=user)

            success_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
            }
            return Response(success_msg, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR,
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pk, *args, **kwargs):
        try:
            role = UserRole.objects.using(DB_NAME).filter(id=pk).first()

            if not role:
                error_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND,
                }
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

            role.delete(using=DB_NAME)

            success_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
            }
            return Response(success_msg, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR,
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
