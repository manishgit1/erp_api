from rest_framework.views import APIView
from master.models import ClientMaster,ContactMaster
from django.conf import settings
from master.serializers import GlobalContactSerializer, ClientMasterSerializer
from datetime import datetime
from rest_framework.serializers import ValidationError
from master import globalparameters
from rest_framework.response import Response
from rest_framework import status
import logging
from nepali_date_utils.date_converter import converter
import json
import ast
from master.global_validation import validate_for_obj
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication
from crm.models import LeadQuotation, LeadQuotationDocuments

logger = logging.getLogger('django')

DB_NAME = settings.DB_NAME

def get_next_client_code(db_name):
    try:
        # Get all client codes that are digits
        client_codes = ClientMaster.objects.using(db_name).values_list('client_code', flat=True)
        numeric_codes = [int(code) for code in client_codes if code and code.isdigit()]
        
        # Start from 24578 if no numeric codes found or all are smaller
        start_range = 24578
        if not numeric_codes:
            return str(start_range)
        
        max_code = max(numeric_codes)
        if max_code < start_range:
            return str(start_range)
        
        return str(max_code + 1)
    except Exception as e:
        logger.error(f"Error generating client code: {str(e)}")
        # Fallback to a semi-random/safe start if query fails
        return "24578"

class ClientMasterCreateAPIView(APIView):

#    permission_classes = [IsAuthenticated]
#    authentication_classes = [TokenAuthentication]
   
   def post(self,request,*args,**kwargs):
    try:
       # if request.data['citizenshipIssuedDateAd']:
       #    request.data['citizenshipIssuedDateBs'] = converter.ad_to_bs(str(request.data['citizenshipIssuedDateAd']))
       #    request.data['citizenshipIssuedDateAd'] = datetime.strftime(datetime.strptime(str(request.data['citizenshipIssuedDateAd']), '%Y/%M/%d'), '%Y-%M-%d')
       
       # Convert dates if needed, or rely on frontend sending YYYY-MM-DD
       # Request data might need date conversion if format is different

       user = globalparameters.validation_for_authentication_parameters(request)

       json_error = []
       
       client_code = get_next_client_code(DB_NAME)

       mobile_number = str(request.data['clientMasterMobileNumber']).strip()
       if ClientMaster.objects.using(DB_NAME).filter(mobile_number=mobile_number,is_void=False).exists():
           json_error.append("Client already exists")

       if json_error:
           return Response({
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_BAD_REQUEST,
               globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_BAD_REQUEST,
               "errors": json_error
           }, status=status.HTTP_400_BAD_REQUEST)

       global_contact = ContactMaster.objects.using(DB_NAME).filter(mobile_number=mobile_number,is_void=False).first()
    #    if global_contact:
    #        global_contact.is_client = True
    #        global_contact.save()

       serializer = ClientMasterSerializer(data=request.data, context={'db_name':DB_NAME})
       serializer.is_valid(raise_exception=True)
       serializer.save(created_at=datetime.now(),created_by=user.id, client_code=client_code,global_contact=global_contact)

       success_msg = {       
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS  
       }
       return Response(success_msg, status=status.HTTP_200_OK)
    

    except Exception as exc: 
        logger.error(str(exc), exc_info=True)
        error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
        }
        return Response(error_msg,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClientMasterListAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            contacts = ClientMaster.objects.using(DB_NAME).filter(is_void=False)
            serializer = ClientMasterSerializer(
                contacts, many=True, context={"db_name": DB_NAME}
            )
            
            response = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": serializer.data
            }


            return Response(response, status=status.HTTP_200_OK)      

        except Exception as exc: 
            logger.error(str(exc), exc_info=True)
            error_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckIfClientMasterExistsAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request,format=None):

        data = json.loads(json.dumps(ast.literal_eval(request.GET.get('jsonData'))))
        mobile_number = str(data['mobileNumber']).strip() if 'mobileNumber' in data else ''
        try:

            client_master = ClientMaster.objects.using(DB_NAME).filter(mobile_number=mobile_number,is_void=False)
            if client_master.exists():
                client_master = client_master.first()                
                response_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                    "clientExists": True,
                    "clientData": {
                        "referenceId": client_master.reference_id,
                        "clientName": client_master.full_name,
                        "clientCode": client_master.client_code
                    }
                }
                return Response(response_msg, status=status.HTTP_200_OK)
            else:
                
                contact_master = ContactMaster.objects.using(DB_NAME).filter(mobile_number=mobile_number,is_void=False)
                if contact_master.exists():
                   contact_master = contact_master.first()
                   contact_serializer = GlobalContactSerializer(contact_master,context={'db_name':DB_NAME, 'model_class': ContactMaster} )
                   response_msg = {
                      globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                      globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                      "clientExists": False,
                      "clientData": contact_serializer.data
                   }

                   return Response(response_msg,status=status.HTTP_200_OK)
                   
                response_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DATA_NOT_FOUND
                }
                return Response(response_msg, status=status.HTTP_404_NOT_FOUND)
        
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


class ClientMasterDataByIdAPIView(APIView):

    def get(self, request, pk,*args, **kwargs):
        contacts = ClientMaster.objects.using(DB_NAME).filter(is_void=False,reference_id=pk).first()
        serializer = ClientMasterSerializer(
            contacts, context={"db_name": DB_NAME}
        )
        
        response = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
            "datas": serializer.data
        }

        return Response(response, status=status.HTTP_200_OK)      


class ClientMasterEditAPIView(APIView):
   
   def post(self,request,pk,*args,**kwargs):
    try:
       client_master = ClientMaster.objects.using(DB_NAME).filter(is_void=False,reference_id=pk).first()
       serializer = ClientMasterSerializer(instance=client_master,data=request.data,partial=True ,context={'db_name':DB_NAME})
       serializer.is_valid(raise_exception=True)
       serializer.save(updated_at=datetime.now())

       success_msg = {       
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS  
       }
       return Response(success_msg, status=status.HTTP_200_OK)
    
    except ValidationError as exc:
        logger.error(str(exc), exc_info=True)
        return Response({"status": "error", "message": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as exc:
        logger.error(str(exc), exc_info=True)
        error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
        
        return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ClientMasterGetLeadDataAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication,]

    def get(self, request, format=None):
        try:

            _ =globalparameters.validation_for_authentication_parameters(request)
            json_error = []

            data = json.loads(json.dumps(ast.literal_eval(request.GET.get('jsonData'))))

            logger.info(str(data),exc_info=True)

            reference_id = str(data['referenceId']).strip() if 'referenceId' in data else ''

            # client_master,client_master_error =validate_for_obj(reference_id,DB_NAME,ClientMaster,'Client Master')
            # json_error.extend(client_master_error)

            lead_quotation,lead_quotation_error = validate_for_obj(reference_id,DB_NAME,LeadQuotation,'Lead Quotation')
            json_error.extend(lead_quotation_error)
            if json_error:
                error_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
                    globalparameters.RESULT_ERROR: json_error
                }
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            client_master = ClientMaster.objects.using(DB_NAME).filter(is_void=False,global_contact=lead_quotation.contact)
 
            if not client_master:
                json_error.append("KYC data not found")
                error_msg = {
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
                    globalparameters.RESULT_ERROR: json_error
                }
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            #retrieve first instance of client master
            client_master = client_master.first()

            client_data = {
                'clientCode': client_master.client_code,
                'clientName': client_master.full_name,
                'clientMobileNumber': client_master.mobile_number,
                'clientPermanentAddress': client_master.permanent_address,
                'clientCitizenshipNumber': client_master.citizenship_number,
                'loanAmount': lead_quotation.loan_amount,
                'loanTenure': lead_quotation.tenure,
                'loanInterestRate': lead_quotation.interest_rate,
                'loanType': lead_quotation.loan_type.reference_id if lead_quotation.loan_type_id else '',
                'clientTemporaryAddress': client_master.temporary_address if client_master.temp_municipality_id else ''
            }

            # fetch lead documents
            lead_documents = LeadQuotationDocuments.objects.using(DB_NAME).filter(lead_id=lead_quotation.id, is_void=False)
            document_images = []
            for doc in lead_documents:
                img_base64 = globalparameters.get_image_from_drive(DB_NAME, 'lead_quotation', doc.file_name)
                if img_base64:
                    document_images.append({
                        'imageValue': img_base64
                    })
            
            client_data['documentImages'] = document_images

            return Response(client_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


