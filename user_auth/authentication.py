from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user_auth.models import User

class TempSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # DRF converts HTTP_TEMP_SESSION_ID header to META['HTTP_TEMP_SESSION_ID']
        temp_session_id = request.META.get('HTTP_TEMP_SESSION_ID')

        if not temp_session_id:
            return None

        try:
            user = User.objects.get(temp_session_id=temp_session_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid session ID')

        # Returning (user, None) tells DRF that this request is authenticated
        return (user, None)
