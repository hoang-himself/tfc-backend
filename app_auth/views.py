from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST

    refresh_token = request.POST.get('refresh')

    if (refresh_token is None or refresh_token == ''):
        response.data = {
            "refresh": ['This field is required']
        }
        return response

    try:
        refresh = RefreshToken(refresh_token)
    except TokenError:
        response.data = {
            "detail": "Token has wrong type",
            "code": "token_not_valid"
        }
        return response

    refresh.blacklist()

    response.status_code = status.HTTP_204_NO_CONTENT
    response.data = {
        "result": "ok"
    }

    return response
