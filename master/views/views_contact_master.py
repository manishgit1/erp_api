from rest_framework.views import APIView
from master.models import ContactMaster
from django.conf import settings
from master.serializers import GlobalContactSerializer
from datetime import datetime
from rest_framework.serializers import ValidationError
from master import globalparameters
from rest_framework.response import Response
from rest_framework import status
import logging
from nepali_date_utils.date_converter import converter
import json
import ast

logger = logging.getLogger('django')

DB_NAME = settings.DB_NAME

class ContactMasterCreateAPIView(APIView):
   
   def post(self,request,*args,**kwargs):
    try:
       if request.data['citizenshipIssuedDateAd']:
          request.data['citizenshipIssuedDateBs'] = converter.ad_to_bs(str(request.data['citizenshipIssuedDateAd']))
          request.data['citizenshipIssuedDateAd'] = datetime.strftime(datetime.strptime(str(request.data['citizenshipIssuedDateAd']), '%Y/%M/%d'), '%Y-%M-%d')
       serializer = GlobalContactSerializer(data=request.data, context={'db_name':DB_NAME, 'model_class': ContactMaster})
       serializer.is_valid(raise_exception=True)
       serializer.save(created_at=datetime.now())

       success_msg = {       
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS  
       }
       return Response(success_msg, status=status.HTTP_200_OK)
    
    except ValidationError as exc:
        logger.error(str(exc), exc_info=True)
        error_msg = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_VALIDATION_ERROR,
            globalparameters.RESULT_DESCRIPTION: str(exc.detail)
        }
        return Response(error_msg,status=status.HTTP_400_BAD_REQUEST)

    except Exception as exc: 
        logger.error(str(exc), exc_info=True)
        error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
        return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GlobalContactListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        contacts = ContactMaster.objects.using(DB_NAME).filter(is_void=False)
        serializer = GlobalContactSerializer(
            contacts, many=True, context={"db_name": DB_NAME}
        )

        # serializer.is_valid(raise_exception=True)
        
        response = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
            "datas": serializer.data
        }


        return Response(response, status=status.HTTP_200_OK)      


class CheckIfGlobalContactExistsAPIView(APIView):

    def get(self,request,format=None):

        data = json.loads(json.dumps(ast.literal_eval(request.GET.get('jsonData'))))
        mobile_number = str(data['mobileNumber']).strip() if 'mobileNumber' in data else ''
        try:

            contact = ContactMaster.objects.using(DB_NAME).filter(mobile_number=mobile_number)
            if contact.exists():
                contact = contact.first()
                contact_serializer = GlobalContactSerializer(contact,context={'db_name':DB_NAME, 'model_class': ContactMaster} )
                
                response_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                    "globalContactData": contact_serializer.data 
                }
                return Response(response_msg, status=status.HTTP_200_OK)
            else:
                response_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND
                }
                return Response(response_msg, status=status.HTTP_200_OK)
        
        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(response_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class GlobalContactDataByIdAPIView(APIView):

    def get(self, request, pk,*args, **kwargs):
        contacts = ContactMaster.objects.using(DB_NAME).filter(is_void=False,reference_id=pk).first()
        serializer = GlobalContactSerializer(
            contacts, context={"db_name": DB_NAME}
        )

        # serializer.is_valid(raise_exception=True)
        
        response = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
            "datas": serializer.data
        }


        return Response(response, status=status.HTTP_200_OK)      



class ContactMasterEditAPIView(APIView):
   
   def post(self,request,pk,*args,**kwargs):
    try:
       if request.data['citizenshipIssuedDateAd']:
          request.data['citizenshipIssuedDateBs'] = converter.ad_to_bs(str(request.data['citizenshipIssuedDateAd']))
          request.data['citizenshipIssuedDateAd'] = datetime.strftime(datetime.strptime(str(request.data['citizenshipIssuedDateAd']), '%Y/%M/%d'), '%Y-%M-%d')
       contact_master = ContactMaster.objects.using(DB_NAME).filter(is_void=False,reference_id=pk).first()
       serializer = GlobalContactSerializer(instance=contact_master,data=request.data,partial=True ,context={'db_name':DB_NAME, 'model_class': ContactMaster})
       serializer.is_valid(raise_exception=True)
       serializer.save(created_at=datetime.now())

       success_msg = {       
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS  
       }
       return Response(success_msg, status=status.HTTP_200_OK)
    
    except ValidationError as exc:
        logger.error(str(exc), exc_info=True)
        raise ValidationError(self,exc.message)
    
    except Exception as exc:
        logger.error(str(exc), exc_info=True)
        error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
        
        return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)