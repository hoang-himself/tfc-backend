from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def ping(request):
    response = Response()

    response.status = status.HTTP_200_OK
    response.data = {
        "pong"
    }

    return response
