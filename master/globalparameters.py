from rest_framework.exceptions import AuthenticationFailed
from user_auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.http import JsonResponse
from django.db import connections, transaction, DatabaseError
from rest_framework.response import Response
from rest_framework import status
from master.models import generate_uuid
import os
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
import base64
try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad
except ImportError:
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
    except ImportError:
        AES = None
        unpad = None
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from datetime import datetime


logger = logging.getLogger('django')


RESULT_CODE = "resultCode"
RESULT_DESCRIPTION = "resultDescription"

RESULT_ERROR = "errorMessage"

RESULT_CODE_SUCCESS = '0'
RESULT_ERROR_CODE = "-100"
RESULT_ERROR_CONNECTION_CODE = "-112"
RESULT_CODE_INVALID_PARAMS = "-110"
RESULT_CODE_INVALID_CREDENTIALS = '-104'
RESULT_CODE_INTERNAL_SERVER_ERROR = '-108'
RESULT_CODE_DATA_NOT_FOUND = '-106'

RESULT_VALIDATION_ERROR = "-105"

RESULT_INTERNAL_SERVER_ERROR = "Internal Server Error"
RESULT_DESCRIPTION_INVALID_PARAMS = "Invalid Request Parameters"
RESULT_DESCRIPTION_SUCCESS = "Success"
RESULT_CONNECTION_ERROR = "Database Connection Failed"
RESULT_DESCRIPTION_INVALID_CREDENTIALS = "Invalid Credentials"
RESULT_DATA_NOT_FOUND = 'Data Not Found'
RESULT_SESSION_EXPIRED = "Session Expired"


def execute_raw_sql(request, query, params=None, db_name='default'):
    """
    Execute raw SQL query (insert/procedure call) dynamically 
    and return a DRF Response directly.
    """
    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute(query, params or [])
            result_status = None
            try:
                result = cursor.fetchone()
                if result:
                    result_status = result[0] if len(result) == 1 else result
            except Exception as exc:
               logger.error(str(exc), exc_info= True)
               response_msg = {
                   RESULT_CODE: RESULT_CODE_INTERNAL_SERVER_ERROR,
                   RESULT_DESCRIPTION: RESULT_INTERNAL_SERVER_ERROR
               }
               return Response(response_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            rows_affected = cursor.rowcount
            transaction.commit(using=db_name)
            response_msg = {
                RESULT_CODE: RESULT_CODE_SUCCESS,
                RESULT_DESCRIPTION: RESULT_DESCRIPTION_SUCCESS,
                "success": True,
                "status": result_status,
                "rows_affected": rows_affected,
            }
            return Response(response_msg, status=status.HTTP_200_OK)

    except DatabaseError as e:
        transaction.rollback(using=db_name)
        response_msg = {
            RESULT_CODE: RESULT_CODE_INTERNAL_SERVER_ERROR,
            RESULT_DESCRIPTION: RESULT_INTERNAL_SERVER_ERROR,
            "success": False,
            "error": str(e),
        }
        return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)



def save_image_to_drive(file: UploadedFile, main_folder: str, custom_folder: str, file_name:str):
    """
    Save an uploaded image to the project-level drive.
    
    Args:
        file (UploadedFile): The uploaded file from request.FILES.
        main_folder (str): The main folder at project level (e.g., 'media').
        custom_folder (str): Subfolder inside main_folder (e.g., 'customer_docs').
    
    Returns:
        str: Relative file path where image is saved (for DB reference).
    """
    
    if not file:
        raise ValueError("No file provided.")
    
    if  "," in file:
        header, file_value = str(file).split(',',1)
    else:
        file_value = file
        header = ""

    extension = ".png"
    # if "image/jpeg" in header:
    #     extension = '.jpg'
    # elif "image/png" in header:
    #     extension = '.png'

    
    try:
        file_bytes = base64.b64decode(file_value)
    except Exception as e:
        raise ValueError('Invalid Base64 data for' , e)
    
    project_root = settings.BASE_DIR 
    main_folder_path = os.path.join(project_root, main_folder)
    if not os.path.exists(main_folder_path):
        os.makedirs(main_folder_path, exist_ok=True)

    target_folder_path = os.path.join(main_folder_path, custom_folder)
    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path, exist_ok=True)

    file_name = f'{file_name}{extension}'

    full_path = os.path.join(target_folder_path, file_name)
    with open(full_path, "wb") as f:
        f.write(file_bytes)
   #  relative_path = os.path.join(custom_folder, file_name)
   #  return relative_path


def get_image_from_drive(db_name: str, folder: str, file_name: str):
    """
    Returns base64-encoded string of the image file if exists, otherwise None.
    db_name: subfolder for database/project
    folder: folder name under db_name
    file_name: filename without extension
    """
    # Build full path (assuming PNG)
    file_path = os.path.join(settings.BASE_DIR, db_name, folder, f"{file_name}.png")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
                # Return in a format ready for <img src="data:image/png;base64,..." />
                return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            print(f"Error encoding image {file_path}: {e}")
            return None
    return None




class CustomAPIException(APIException):
    def __init__(self, result_code, result_description, status_code=status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.detail = {
            RESULT_CODE: result_code,
            RESULT_DESCRIPTION: result_description
        }
        super().__init__(self.detail, status_code)

    @staticmethod
    def handle(exc, context):
        response = exception_handler(exc, context)

        if response is not None:
            if isinstance(exc, CustomAPIException):
                response.data = exc.detail
            elif isinstance(response.data, dict):
                # Handle standard DRF exceptions (ValidationError, AuthenticationFailed, etc.)
                if 'detail' in response.data:
                    # Simple detail string (e.g. 401, 403, 404)
                    response.data = {
                        RESULT_CODE: RESULT_ERROR_CODE,
                        RESULT_DESCRIPTION: str(response.data['detail'])
                    }
                else:
                    # Field-specific validation errors
                    first_key = next(iter(response.data))
                    first_error = response.data[first_key]
                    
                    if isinstance(first_error, list) and len(first_error) > 0:
                        error_desc = str(first_error[0])
                    else:
                        error_desc = str(first_error)
                    
                    response.data = {
                        RESULT_CODE: RESULT_VALIDATION_ERROR,
                        RESULT_DESCRIPTION: error_desc
                    }
            elif isinstance(response.data, list) and len(response.data) > 0:
                response.data = {
                    RESULT_CODE: RESULT_ERROR_CODE,
                    RESULT_DESCRIPTION: str(response.data[0])
                }

        return response


def custom_exception_handler(exc, context):
    return CustomAPIException.handle(exc, context)


def validation_for_authentication_parameters(request):
   try:
        # If user is already authenticated by DRF authentication classes, return it
        if request.user and request.user.is_authenticated:
            return request.user

        # temp_session_id  = request.META.get('HTTP_TEMP_SESSION_ID')

        # if not temp_session_id:
        #     raise AuthenticationFailed('missing authentication headers')
        
        # user = User.objects.get(temp_session_id=temp_session_id)
        
        # if user:
        #     # Populate request.user for manual calls
        #     request.user = user
        #     return user
   
   except ObjectDoesNotExist as e:
      logger.error(str(e), exc_info=True)
      error_msg = {
         RESULT_CODE : RESULT_CODE_INVALID_CREDENTIALS,
         RESULT_DESCRIPTION : RESULT_DESCRIPTION_INVALID_CREDENTIALS
      }

      return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
   
   except Exception as e:
      logger.error(str(e), exc_info=True)
      error_msg = {
         RESULT_CODE : RESULT_CODE_INTERNAL_SERVER_ERROR,
         RESULT_DESCRIPTION : RESULT_INTERNAL_SERVER_ERROR
      }
      return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def get_general_json_parameters(request):
    return {
        'created_at': str(datetime.now()),
        'created_by': request.user.id,
        'updated_at': str(datetime.now()),
        'updated_by': request.user.id,
    }


def decrypt_payload(encrypted_payload, key_str="1234567890123456"):
    """
    Decrypts a base64 encoded, AES-CBC encrypted payload.
    Payload format: base64(iv + ciphertext)
    """
    if AES is None or unpad is None:
        logger.warning("Decryption skipped: Cryptodome/Crypto library not found.")
        return None

    try:
        # Decode base64
        encrypted_data = base64.b64decode(encrypted_payload)
        
        # Extract IV (first 16 bytes) and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Decrypt
        key = key_str.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}", exc_info=True)
        return None



