from rest_framework import (exceptions, status)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['uuid'] = str(user.uuid)
        token['groups'] = str(user.groups)

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class AuthView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        refresh_token = request.POST.get('refresh', None)

        if not (refresh_token):
            raise exceptions.ValidationError(
                {'refresh': 'This field is required.'}
            )

        response = Response()
        # RefreshToken(refresh_token).blacklist()
        response.status_code = status.HTTP_200_OK
        response.data = {'detail': 'Ok'}
        return response
